# ── SOW DESIGN COMPARE ENDPOINT ───────────────────────────
# Add this route to /root/podio-sync/server.py on the VPS
# Compares proposal (Customer Docs) vs planset (Approved folder)
# Extracts panel layout, equipment, and system specs from both PDFs
# REQUIRES: pip install PyMuPDF  (provides the 'fitz' module for PDF→PNG thumbnails)

@app.route("/sow-design-compare", methods=["POST"])
def sow_design_compare():
    """Compare proposal PDF vs planset PDF for a SOW item.
    Extracts equipment and layout from both, returns comparison."""
    try:
        data = request.get_json(silent=True) or {}
        sow_item_id = data.get("sow_item_id")
        if not sow_item_id:
            return jsonify({"status": "error", "message": "sow_item_id required"}), 400

        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload
        import io, base64, re, anthropic, pypdf, tempfile, os
        import json as json2

        # ── GET SOW ITEM → LINKED PROJECT ────────────────────
        token = get_podio_token()
        sow_res = requests.get(
            f"https://api.podio.com/item/{sow_item_id}",
            headers=ph(token)
        )
        sow = sow_res.json()
        sow_fields = sow.get("fields", [])

        # Get project item
        project_item_id = None
        for f in sow_fields:
            if f.get("field_id") == 266487957:
                vals = f.get("values", [])
                if vals:
                    project_item_id = vals[0]["value"]["item_id"]
                break
        if not project_item_id:
            return jsonify({"status": "error", "message": "No linked project found"}), 400

        # Get project fields for folder IDs
        proj_res = requests.get(
            f"https://api.podio.com/item/{project_item_id}",
            headers=ph(token)
        )
        proj = proj_res.json()
        proj_fields = proj.get("fields", [])

        def pfv(fid):
            f = next((f for f in proj_fields if f.get("field_id") == fid), None)
            if not f or not f.get("values"):
                return None
            v = f["values"][0]
            if "value" in v:
                val = v["value"]
                if isinstance(val, dict):
                    return val.get("text") or val.get("name")
                return val
            return None

        # Folder IDs
        customer_fid = pfv(266618731)  # Customer Docs
        approved_fid = pfv(268981903)  # Approved

        if not customer_fid and not approved_fid:
            return jsonify({"status": "error", "message": "No Drive folders found"}), 400

        # ── GOOGLE DRIVE ACCESS ───────────────────────────────
        creds = service_account.Credentials.from_service_account_file(
            "/root/service_account.json",
            scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        drive = build("drive", "v3", credentials=creds)

        def list_folder(folder_id):
            if not folder_id:
                return []
            try:
                r = drive.files().list(
                    q=f"'{folder_id}' in parents",
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                    fields="files(id,name,mimeType,size)"
                ).execute()
                return r.get("files", [])
            except:
                return []

        def download_file(file_id):
            buf = io.BytesIO()
            req = drive.files().get_media(fileId=file_id)
            dl = MediaIoBaseDownload(buf, req)
            done = False
            while not done:
                _, done = dl.next_chunk()
            return buf.getvalue()

        def truncate_pdf(pdf_data, max_pages=8):
            """Keep only first N pages of a PDF."""
            try:
                reader = pypdf.PdfReader(io.BytesIO(pdf_data))
                writer = pypdf.PdfWriter()
                pages = min(max_pages, len(reader.pages))
                for i in range(pages):
                    writer.add_page(reader.pages[i])
                tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
                writer.write(tmp)
                tmp.close()
                with open(tmp.name, "rb") as f:
                    result = f.read()
                os.unlink(tmp.name)
                return result
            except:
                return pdf_data

        # ── FIND PDFS ────────────────────────────────────────
        result = {"proposal": None, "planset": None}

        # Find proposal in Customer Docs (filename pattern: Name_Design_N_Aveyo_date.pdf)
        if customer_fid:
            cust_files = list_folder(customer_fid)
            cust_pdfs = [f for f in cust_files if f.get("mimeType") == "application/pdf"]
            # Look for design/proposal files
            proposal_file = None
            for f in cust_pdfs:
                name = f["name"].lower()
                if "design" in name or "proposal" in name or "aurora" in name:
                    proposal_file = f
                    break
            # Fallback: newest PDF
            if not proposal_file and cust_pdfs:
                proposal_file = cust_pdfs[0]

            if proposal_file:
                result["proposal_file"] = proposal_file["name"]

        # Find planset in Approved folder (filename contains 'plan')
        if approved_fid:
            appr_files = list_folder(approved_fid)
            appr_pdfs = [f for f in appr_files if f.get("mimeType") == "application/pdf"]
            planset_file = None
            for f in appr_pdfs:
                name = f["name"].lower()
                if "plan" in name:
                    planset_file = f
                    break
            if not planset_file and appr_pdfs:
                planset_file = appr_pdfs[0]

            if planset_file:
                result["planset_file"] = planset_file["name"]

        # ── EXTRACT FROM BOTH PDFs ────────────────────────────
        extract_prompt = """Analyze this solar project PDF and extract the following in JSON format:
{
  "system_size_kw": <number or null>,
  "panel_manufacturer": "<string or null>",
  "panel_model": "<string or null>",
  "panel_count": <number or null>,
  "panel_wattage": <number or null>,
  "inverter_manufacturer": "<string or null>",
  "inverter_model": "<string or null>",
  "inverter_count": <number or null>,
  "battery_model": "<string or null>",
  "battery_count": <number or null>,
  "mount_type": "<roof mount, ground mount, or null>",
  "estimated_production_kwh": <number or null>,
  "roof_type": "<string or null>",
  "panel_layout_description": "<brief description of where panels are placed on the roof - which roof faces, how many per array, etc.>",
  "layout_page": <1-based page number that shows the panel layout / roof plan diagram, or 1 if not found>
}
Return ONLY valid JSON, no other text."""

        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        def render_page_thumbnail(pdf_data, page_num, max_width=800):
            """Render a specific page of a PDF as a base64 PNG thumbnail.
            page_num is 1-based."""
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(stream=pdf_data, filetype="pdf")
                page_idx = min(page_num - 1, len(doc) - 1)
                page_idx = max(0, page_idx)
                page = doc[page_idx]
                # Scale to max_width while preserving aspect ratio
                zoom = max_width / page.rect.width
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                png_data = pix.tobytes("png")
                doc.close()
                return base64.standard_b64encode(png_data).decode(), page_idx + 1
            except Exception as e:
                print(f"[sow-design-compare] thumbnail render failed: {e}")
                return None, None

        def extract_from_pdf(pdf_data, label):
            pdf_data_truncated = truncate_pdf(pdf_data, 8)
            encoded = base64.standard_b64encode(pdf_data_truncated).decode()
            try:
                msg = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1500,
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": encoded
                                }
                            },
                            {"type": "text", "text": extract_prompt}
                        ]
                    }]
                )
                raw = msg.content[0].text.strip()
                # Clean markdown fences
                raw = re.sub(r"^```(?:json)?\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)
                return json2.loads(raw)
            except Exception as e:
                return {"error": str(e)}

        # Extract from proposal + generate layout thumbnail
        proposal_pdf_data = None
        if proposal_file:
            proposal_pdf_data = download_file(proposal_file["id"])
            result["proposal"] = extract_from_pdf(proposal_pdf_data, "proposal")
            # Render layout page thumbnail
            layout_pg = (result["proposal"] or {}).get("layout_page", 1) or 1
            thumb, actual_pg = render_page_thumbnail(proposal_pdf_data, layout_pg)
            if thumb:
                result["proposal_thumb"] = thumb
                result["proposal_thumb_page"] = actual_pg

        # Extract from planset + generate layout thumbnail
        planset_pdf_data = None
        if planset_file:
            planset_pdf_data = download_file(planset_file["id"])
            result["planset"] = extract_from_pdf(planset_pdf_data, "planset")
            # Render layout page thumbnail
            layout_pg = (result["planset"] or {}).get("layout_page", 1) or 1
            thumb, actual_pg = render_page_thumbnail(planset_pdf_data, layout_pg)
            if thumb:
                result["planset_thumb"] = thumb
                result["planset_thumb_page"] = actual_pg

        # ── COMPARE ──────────────────────────────────────────
        if result["proposal"] and result["planset"]:
            p = result["proposal"]
            s = result["planset"]
            checks = {}

            # System size
            if p.get("system_size_kw") and s.get("system_size_kw"):
                checks["system_size"] = {
                    "proposal": p["system_size_kw"],
                    "planset": s["system_size_kw"],
                    "match": abs(float(p["system_size_kw"]) - float(s["system_size_kw"])) < 0.5
                }

            # Panel model
            if p.get("panel_model") and s.get("panel_model"):
                checks["panel_model"] = {
                    "proposal": p["panel_model"],
                    "planset": s["panel_model"],
                    "match": p["panel_model"].lower().replace(" ", "") == s["panel_model"].lower().replace(" ", "")
                }

            # Panel count
            if p.get("panel_count") and s.get("panel_count"):
                checks["panel_count"] = {
                    "proposal": p["panel_count"],
                    "planset": s["panel_count"],
                    "match": int(p["panel_count"]) == int(s["panel_count"])
                }

            # Inverter model
            if p.get("inverter_model") and s.get("inverter_model"):
                checks["inverter_model"] = {
                    "proposal": p["inverter_model"],
                    "planset": s["inverter_model"],
                    "match": p["inverter_model"].lower().replace(" ", "") == s["inverter_model"].lower().replace(" ", "")
                }

            # Inverter count
            if p.get("inverter_count") and s.get("inverter_count"):
                checks["inverter_count"] = {
                    "proposal": p["inverter_count"],
                    "planset": s["inverter_count"],
                    "match": int(p["inverter_count"]) == int(s["inverter_count"])
                }

            # Layout description comparison
            if p.get("panel_layout_description") and s.get("panel_layout_description"):
                checks["layout"] = {
                    "proposal": p["panel_layout_description"],
                    "planset": s["panel_layout_description"]
                }

            result["checks"] = checks
            result["all_match"] = all(
                c.get("match", True) for c in checks.values()
                if "match" in c
            )

        result["status"] = "ok"
        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500
