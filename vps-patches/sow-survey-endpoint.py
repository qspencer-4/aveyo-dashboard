
# ── SOW SITE SURVEY REVIEW ─────────────────────────────────
@app.route("/sow-survey-review", methods=["POST"])
def sow_survey_review():
    """Extract roof and tilt photos from site survey PDF."""
    try:
        data = request.get_json(silent=True) or {}
        sow_item_id = data.get("sow_item_id")
        if not sow_item_id:
            return jsonify({"status":"error","message":"sow_item_id required"}), 400

        from google.oauth2 import service_account as sa3
        from googleapiclient.discovery import build as gbuild3
        from googleapiclient.http import MediaIoBaseDownload
        import io, base64, fitz

        token = get_podio_token()
        sow_res = requests.get(f"https://api.podio.com/item/{sow_item_id}", headers=ph(token))
        sow_fields = sow_res.json().get("fields", [])

        project_item_id = None
        for f in sow_fields:
            if f.get("field_id") == 266487957:
                vals = f.get("values", [])
                if vals: project_item_id = vals[0]["value"]["item_id"]
                break
        if not project_item_id:
            return jsonify({"status":"error","message":"No linked project"}), 400

        proj_res = requests.get(f"https://api.podio.com/item/{project_item_id}", headers=ph(token))
        proj_fields = proj_res.json().get("fields", [])

        def pfv3(fid):
            f = next((f for f in proj_fields if f.get("field_id")==fid), None)
            if not f or not f.get("values"): return None
            v = f["values"][0]
            if "value" in v:
                val = v["value"]
                if isinstance(val, dict): return val.get("text") or val.get("name")
                return val
            return None

        survey_fid = pfv3(266618728)
        if not survey_fid:
            return jsonify({"status":"error","message":"No site survey folder"}), 400

        creds3 = sa3.Credentials.from_service_account_file("/root/service_account.json", scopes=["https://www.googleapis.com/auth/drive.readonly"])
        drv3 = gbuild3("drive", "v3", credentials=creds3)

        def lf3(folder_id):
            if not folder_id: return []
            try:
                r = drv3.files().list(q=f"'{folder_id}' in parents", supportsAllDrives=True, includeItemsFromAllDrives=True, fields="files(id,name,mimeType,size)").execute()
                return r.get("files", [])
            except: return []

        def dl3(file_id):
            buf = io.BytesIO()
            req3 = drv3.files().get_media(fileId=file_id)
            d = MediaIoBaseDownload(buf, req3)
            done = False
            while not done: _, done = d.next_chunk()
            return buf.getvalue()

        # Find survey PDF
        survey_files = lf3(survey_fid)
        survey_pdfs = [f for f in survey_files if f.get("mimeType") == "application/pdf"]
        survey_file = None
        for f in survey_pdfs:
            nm = f["name"].lower()
            if "ss" in nm or "survey" in nm or "report" in nm or "companycam" in nm:
                survey_file = f; break
        if not survey_file and survey_pdfs:
            survey_file = survey_pdfs[0]

        if not survey_file:
            return jsonify({"status":"error","message":"No site survey PDF found"}), 400

        pdf_data = dl3(survey_file["id"])
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        total_pages = len(doc)

        result = {
            "status": "ok",
            "file_name": survey_file["name"],
            "total_pages": total_pages,
            "pages": []
        }

        # Identify roof and tilt pages by text content and render thumbnails
        roof_keywords = ["roof", "aerial", "overhead", "drone", "top", "bird"]
        tilt_keywords = ["tilt", "pitch", "angle", "slope", "rafter", "truss", "attic"]
        panel_keywords = ["panel", "meter", "electrical", "breaker", "disconnect", "msp"]

        for i in range(total_pages):
            text = doc[i].get_text().lower()
            imgs = len(doc[i].get_images())

            # Score each page for category
            roof_score = sum(1 for kw in roof_keywords if kw in text) + (1 if imgs > 0 else 0)
            tilt_score = sum(1 for kw in tilt_keywords if kw in text)
            panel_score = sum(1 for kw in panel_keywords if kw in text)

            # Determine page type
            page_type = "other"
            if roof_score >= 2: page_type = "roof"
            elif tilt_score >= 1: page_type = "tilt"
            elif panel_score >= 1: page_type = "electrical"

            # Render thumbnail
            mat = fitz.Matrix(0.4, 0.4)
            pix = doc[i].get_pixmap(matrix=mat)
            thumb = base64.b64encode(pix.tobytes("png")).decode()

            result["pages"].append({
                "page": i + 1,
                "type": page_type,
                "thumb": thumb,
                "text_preview": text[:80].strip()
            })

        doc.close()

        # Also find roof and tilt pages specifically
        result["roof_pages"] = [p for p in result["pages"] if p["type"] == "roof"]
        result["tilt_pages"] = [p for p in result["pages"] if p["type"] == "tilt"]

        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status":"error","message":str(e)}), 500

