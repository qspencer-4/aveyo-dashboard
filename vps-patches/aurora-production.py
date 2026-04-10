# ── AURORA PRODUCTION ENDPOINT (ENHANCED) ─────────────────
# Add this route to /root/podio-sync/server.py on the VPS
# Pulls sold milestone design from Aurora Solar API:
#   layout, inverters, roof measurements, lidar/shade, production
#
# Requires: AURORA_API_KEY and AURORA_TENANT_ID in environment or config
# Aurora API docs: https://docs.aurorasolar.com/reference

@app.route("/aurora-production", methods=["POST"])
def aurora_production():
    """Look up Aurora project by customer name, pull sold design data."""
    try:
        import json as json2

        data = request.get_json(silent=True) or {}
        customer_name = data.get("customer_name", "").strip()
        if not customer_name:
            return jsonify({"status": "error", "message": "customer_name required"}), 400

        AURORA_KEY = os.environ.get("AURORA_API_KEY", AURORA_API_KEY)
        AURORA_TENANT = os.environ.get("AURORA_TENANT_ID", AURORA_TENANT_ID)
        BASE = "https://api-sync.aurorasolar.com"
        headers = {
            "Authorization": f"Bearer {AURORA_KEY}",
            "Content-Type": "application/json"
        }

        # ── FIND PROJECT BY CUSTOMER NAME ─────────────────────
        def find_project(name):
            """Search Aurora projects for matching customer name."""
            page = 1
            while True:
                r = requests.get(
                    f"{BASE}/tenants/{AURORA_TENANT}/projects",
                    headers=headers,
                    params={"page": page, "per_page": 250}
                )
                if r.status_code != 200:
                    break
                projects = r.json().get("projects", [])
                if not projects:
                    break
                # Match by customer name (case-insensitive partial match)
                name_lower = name.lower()
                for p in projects:
                    p_name = (p.get("name") or "").lower()
                    p_customer = (p.get("customer_name") or "").lower()
                    if name_lower in p_name or name_lower in p_customer:
                        return p
                page += 1
                # Safety: don't paginate forever
                if page > 20:
                    break
            return None

        project = find_project(customer_name)
        if not project:
            return jsonify({
                "status": "error",
                "message": f"No Aurora project found for '{customer_name}'"
            }), 404

        project_id = project["id"]
        aurora_url = f"https://app.aurorasolar.com/projects/{project_id}"

        # ── GET ALL DESIGNS FOR PROJECT ───────────────────────
        designs_res = requests.get(
            f"{BASE}/tenants/{AURORA_TENANT}/projects/{project_id}/designs",
            headers=headers
        )
        if designs_res.status_code != 200:
            return jsonify({
                "status": "error",
                "message": "Failed to fetch designs from Aurora"
            }), 500

        all_designs = designs_res.json().get("designs", [])
        if not all_designs:
            return jsonify({
                "status": "error",
                "message": "No designs found for this project",
                "aurora_url": aurora_url
            }), 404

        # ── FIND SOLD MILESTONE DESIGN ────────────────────────
        sold_design = None
        for d in all_designs:
            milestone = (d.get("milestone") or "").lower()
            if milestone == "sold":
                sold_design = d
                break

        # Fallback: most recent design if no sold milestone
        if not sold_design:
            sold_design = all_designs[0]

        design_id = sold_design["id"]

        # ── GET FULL DESIGN DETAILS ───────────────────────────
        design_res = requests.get(
            f"{BASE}/tenants/{AURORA_TENANT}/designs/{design_id}",
            headers=headers
        )
        design_data = design_res.json() if design_res.status_code == 200 else {}

        # ── GET ROOF MEASUREMENTS ─────────────────────────────
        roof_res = requests.get(
            f"{BASE}/tenants/{AURORA_TENANT}/designs/{design_id}/roof_summary",
            headers=headers
        )
        roof_data = roof_res.json() if roof_res.status_code == 200 else {}

        # ── PARSE DESIGN DATA ─────────────────────────────────

        # Arrays / layout info
        arrays_raw = design_data.get("arrays", "[]")
        if isinstance(arrays_raw, str):
            try:
                arrays = json2.loads(arrays_raw)
            except:
                arrays = []
        else:
            arrays = arrays_raw if isinstance(arrays_raw, list) else []

        # Build layout summary from arrays
        layout_arrays = []
        total_panels = 0
        panel_model = None
        panel_manufacturer = None
        panel_wattage = None
        for arr in arrays:
            count = arr.get("module_count") or arr.get("num_modules") or 0
            total_panels += count
            azimuth = arr.get("azimuth")
            pitch = arr.get("pitch") or arr.get("tilt")
            model = arr.get("module_model") or arr.get("module") or {}
            if isinstance(model, dict):
                if not panel_model:
                    panel_model = model.get("model") or model.get("name")
                    panel_manufacturer = model.get("manufacturer")
                    panel_wattage = model.get("wattage") or model.get("stc_power")
            elif isinstance(model, str) and not panel_model:
                panel_model = model
            layout_arrays.append({
                "panel_count": count,
                "azimuth": azimuth,
                "pitch": pitch,
                "orientation": arr.get("orientation"),
                "roof_face": arr.get("roof_face_id") or arr.get("roof_face")
            })

        # Inverter info
        inverters_raw = design_data.get("inverters") or design_data.get("mlpe_config") or []
        if isinstance(inverters_raw, str):
            try:
                inverters_raw = json2.loads(inverters_raw)
            except:
                inverters_raw = []
        inverters = []
        for inv in (inverters_raw if isinstance(inverters_raw, list) else []):
            inverters.append({
                "manufacturer": inv.get("manufacturer"),
                "model": inv.get("model") or inv.get("name"),
                "count": inv.get("count") or inv.get("quantity") or 1,
                "type": inv.get("type") or inv.get("inverter_type"),
                "power_rating": inv.get("power_rating") or inv.get("rated_power")
            })

        # Production data
        production_kwh = (
            design_data.get("annual_production_kwh")
            or design_data.get("production_kwh")
            or design_data.get("estimated_production_kwh")
            or sold_design.get("production_kwh")
        )
        system_size_kw = (
            design_data.get("system_size_kw")
            or design_data.get("dc_system_size_kw")
            or sold_design.get("system_size_kw")
        )

        # Monthly production if available
        monthly_production = design_data.get("monthly_production") or []

        # Lidar / irradiance data
        lidar_source = design_data.get("lidar_source") or design_data.get("imagery_source")
        shade_report = design_data.get("shade_report") or {}
        tsrf = design_data.get("tsrf") or shade_report.get("tsrf")
        tof = design_data.get("tof") or shade_report.get("tof")
        annual_irradiance = design_data.get("annual_irradiance") or shade_report.get("annual_irradiance")

        # Roof measurements from roof_summary
        roof = {}
        if roof_data:
            roof = {
                "total_area_sqft": roof_data.get("area"),
                "modules_area_sqft": roof_data.get("modules_area"),
                "pitch": roof_data.get("pitch"),
                "edges": roof_data.get("edges_length") or {},
                "faces": []
            }
            for face in (roof_data.get("faces") or []):
                roof["faces"].append({
                    "area_sqft": face.get("area"),
                    "pitch": face.get("pitch"),
                    "azimuth": face.get("azimuth"),
                    "module_count": face.get("module_count") or face.get("modules_count")
                })

        # ── BUILD DESIGN HISTORY ──────────────────────────────
        design_list = []
        for d in all_designs:
            design_list.append({
                "name": d.get("name") or d.get("id"),
                "milestone": d.get("milestone"),
                "production_kwh": d.get("production_kwh"),
                "system_size_kw": d.get("system_size_kw"),
                "simulation_valid": d.get("simulation_valid", True),
                "is_sold": d.get("id") == design_id
            })

        # ── RETURN RESULT ─────────────────────────────────────
        result = {
            "status": "ok",
            "aurora_url": aurora_url,
            "project_name": project.get("name"),
            "current_design": sold_design.get("name") or "Sold Design",
            "milestone": sold_design.get("milestone") or "unknown",

            # Production
            "current_production_kwh": production_kwh,
            "current_system_size_kw": system_size_kw,
            "monthly_production": monthly_production,

            # Layout
            "total_panels": total_panels,
            "panel_model": panel_model,
            "panel_manufacturer": panel_manufacturer,
            "panel_wattage": panel_wattage,
            "arrays": layout_arrays,

            # Inverters
            "inverters": inverters,

            # Roof
            "roof": roof,

            # Lidar / shade
            "lidar_source": lidar_source,
            "tsrf": tsrf,
            "tof": tof,
            "annual_irradiance": annual_irradiance,

            # Design history
            "designs": design_list,
        }

        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500
