# ── AURORA PRODUCTION ENDPOINT (ENHANCED) ─────────────────
# REPLACES the existing aurora_production function in /root/podio-sync/server.py
# Uses Aurora web login + GraphQL (same auth as existing endpoint)
# Now pulls SOLD MILESTONE design with: layout, inverters, roof, lidar, production
#
# DEPLOY: Replace lines 5619-5750 (the existing aurora-production block) in server.py
#         Then restart: systemctl restart podio-sync

# ── AURORA PRODUCTION CHECK V3 ─────────────────────────────
@app.route("/aurora-production", methods=["POST"])
def aurora_production():
    """Get sold milestone design data from Aurora Solar for a project."""
    try:
        data = request.get_json(silent=True) or {}
        customer_name = data.get("customer_name", "")
        if not customer_name:
            return jsonify({"status": "error", "message": "customer_name required"}), 400

        import re as re2
        import json as json2

        AURORA_EMAIL = "q.spencer@aveyo.com"
        AURORA_PASS = "Clippers3326!"

        session = requests.Session()

        # Step 1: Login to Aurora
        login_page = session.get("https://app.aurorasolar.com/login")
        csrf_match = re2.search(r'name="authenticity_token" value="([^"]+)"', login_page.text)
        if not csrf_match:
            return jsonify({"status": "error", "message": "Could not get Aurora CSRF token"}), 500

        login_resp = session.post("https://app.aurorasolar.com/user_sessions", data={
            "utf8": "\u2713",
            "authenticity_token": csrf_match.group(1),
            "email": AURORA_EMAIL,
            "password": AURORA_PASS,
            "commit": "Log in"
        }, allow_redirects=False)

        home = session.get("https://app.aurorasolar.com/")
        csrf2_match = re2.search(r'csrf-token.*?content="([^"]+)"', home.text)
        csrf2 = csrf2_match.group(1) if csrf2_match else ""

        api_headers = {"X-CSRF-Token": csrf2, "Accept": "application/json", "Content-Type": "application/json"}

        # Step 2: Find project by customer name
        all_projects = []
        for page in range(1, 10):
            resp = session.get(
                f"https://app.aurorasolar.com/api/projects?per_page=100&page={page}",
                headers=api_headers
            )
            pdata = resp.json()
            projects = pdata.get("projects", [])
            all_projects.extend(projects)
            if len(projects) < 100:
                break

        name_parts = [p.lower() for p in customer_name.split() if len(p) > 1]
        best_project = None
        best_score = 0
        for p in all_projects:
            pname = (p.get("name") or "").lower()
            first = (p.get("customer_first_name") or "").lower()
            last = (p.get("customer_last_name") or "").lower()
            full = f"{first} {last}"
            score = sum(1 for part in name_parts if part in pname or part in full)
            if score > best_score:
                best_score = score
                best_project = p

        if not best_project or best_score == 0:
            return jsonify({"status": "error", "message": f"No Aurora project found for '{customer_name}'", "total_projects": len(all_projects)}), 404

        project_id = best_project["id"]

        # Step 3: Get full project with designs
        proj_resp = session.get(
            f"https://app.aurorasolar.com/api/projects/{project_id}",
            headers=api_headers
        )
        proj_data = proj_resp.json()
        project = proj_data.get("project", proj_data)
        designs_list = proj_data.get("designs", [])

        # Step 4: Find SOLD milestone design (fallback to latest)
        sold_design = None
        for d in designs_list:
            milestone = (d.get("milestone") or "").lower()
            if milestone == "sold":
                sold_design = d
                break
        if not sold_design:
            sold_design = designs_list[-1] if designs_list else None

        if not sold_design:
            return jsonify({"status": "error", "message": "No designs found", "aurora_url": f"https://v2.aurorasolar.com/projects/{project_id}"}), 404

        sold_id = sold_design["id"]

        # Step 5: GraphQL — get full sold design details
        gql_query = """
        query SoldDesignDetails($id: ID!) {
          designById(id: $id) {
            id
            name
            masterPerformanceSimulation {
              acPowerAnnual
              acPowerMonthly
              valid
            }
            components {
              type
              manufacturer
              model
              quantity
              attributes
            }
            arrays {
              moduleCount
              azimuth
              tilt
              orientation
              roofFaceId
              module {
                manufacturer
                model
                wattage
              }
            }
            roofSummary {
              totalArea
              modulesArea
              averagePitch
              faces {
                area
                azimuth
                pitch
                moduleCount
              }
              edges {
                eave
                ridge
                hip
                rake
                valley
              }
            }
            lidarSource
            irradianceAnalysis {
              tsrf
              tof
              annualIrradiance
            }
          }
        }
        """

        gql_resp = session.post(
            "https://app.aurorasolar.com/graphql",
            headers=api_headers,
            json={"query": gql_query, "variables": {"id": sold_id}}
        )
        gql_data = gql_resp.json().get("data", {}).get("designById", {})

        # If complex GraphQL fails, fall back to simpler query
        if not gql_data:
            simple_gql = '{ designById(id: "' + sold_id + '") { id name masterPerformanceSimulation { acPowerAnnual valid } } }'
            gql_resp2 = session.post(
                "https://app.aurorasolar.com/graphql",
                headers=api_headers,
                json={"query": simple_gql}
            )
            gql_data = gql_resp2.json().get("data", {}).get("designById", {})

        # Step 6: Also try the REST design endpoint for extra data
        design_rest = {}
        try:
            dr = session.get(
                f"https://app.aurorasolar.com/api/designs/{sold_id}",
                headers=api_headers
            )
            if dr.status_code == 200:
                design_rest = dr.json().get("design", dr.json())
        except:
            pass

        # ── PARSE PRODUCTION ──────────────────────────────────
        sim = gql_data.get("masterPerformanceSimulation") or {}
        production_kwh = None
        if sim.get("acPowerAnnual"):
            production_kwh = round(sim["acPowerAnnual"] / 1000, 1)
        monthly_production = sim.get("acPowerMonthly") or []
        if monthly_production:
            monthly_production = [round(m / 1000, 1) if m else 0 for m in monthly_production]

        system_stc = sold_design.get("system_size_stc")
        system_size_kw = round(system_stc / 1000, 2) if system_stc else None

        # ── PARSE LAYOUT / ARRAYS ─────────────────────────────
        arrays_gql = gql_data.get("arrays") or []
        layout_arrays = []
        total_panels = 0
        panel_model = None
        panel_manufacturer = None
        panel_wattage = None

        for arr in arrays_gql:
            count = arr.get("moduleCount") or 0
            total_panels += count
            mod = arr.get("module") or {}
            if not panel_model and mod:
                panel_model = mod.get("model")
                panel_manufacturer = mod.get("manufacturer")
                panel_wattage = mod.get("wattage")
            layout_arrays.append({
                "panel_count": count,
                "azimuth": arr.get("azimuth"),
                "pitch": arr.get("tilt"),
                "orientation": arr.get("orientation"),
                "roof_face": arr.get("roofFaceId")
            })

        # Fallback: try REST design data for arrays
        if not layout_arrays and design_rest:
            arrays_raw = design_rest.get("arrays") or design_rest.get("module_arrays") or "[]"
            if isinstance(arrays_raw, str):
                try:
                    arrays_parsed = json2.loads(arrays_raw)
                except:
                    arrays_parsed = []
            else:
                arrays_parsed = arrays_raw if isinstance(arrays_raw, list) else []
            for arr in arrays_parsed:
                count = arr.get("module_count") or arr.get("num_modules") or 0
                total_panels += count
                layout_arrays.append({
                    "panel_count": count,
                    "azimuth": arr.get("azimuth"),
                    "pitch": arr.get("pitch") or arr.get("tilt"),
                    "orientation": arr.get("orientation"),
                    "roof_face": arr.get("roof_face_id")
                })

        # ── PARSE INVERTERS ───────────────────────────────────
        inverters = []
        components = gql_data.get("components") or []
        for comp in components:
            ctype = (comp.get("type") or "").lower()
            if "inverter" in ctype or "mlpe" in ctype or "optimizer" in ctype:
                attrs = comp.get("attributes") or {}
                if isinstance(attrs, str):
                    try:
                        attrs = json2.loads(attrs)
                    except:
                        attrs = {}
                inverters.append({
                    "manufacturer": comp.get("manufacturer"),
                    "model": comp.get("model"),
                    "count": comp.get("quantity") or 1,
                    "type": comp.get("type"),
                    "power_rating": attrs.get("power_rating") or attrs.get("rated_power")
                })

        # Fallback: REST design inverter data
        if not inverters and design_rest:
            inv_raw = design_rest.get("inverters") or design_rest.get("mlpe_config") or []
            if isinstance(inv_raw, str):
                try:
                    inv_raw = json2.loads(inv_raw)
                except:
                    inv_raw = []
            for inv in (inv_raw if isinstance(inv_raw, list) else []):
                inverters.append({
                    "manufacturer": inv.get("manufacturer"),
                    "model": inv.get("model") or inv.get("name"),
                    "count": inv.get("count") or inv.get("quantity") or 1,
                    "type": inv.get("type") or inv.get("inverter_type"),
                    "power_rating": inv.get("power_rating")
                })

        # ── PARSE ROOF ────────────────────────────────────────
        roof = {}
        roof_gql = gql_data.get("roofSummary") or {}
        if roof_gql:
            edges = roof_gql.get("edges") or {}
            roof = {
                "total_area_sqft": roof_gql.get("totalArea"),
                "modules_area_sqft": roof_gql.get("modulesArea"),
                "pitch": roof_gql.get("averagePitch"),
                "edges": {
                    "eave": edges.get("eave"),
                    "ridge": edges.get("ridge"),
                    "hip": edges.get("hip"),
                    "rake": edges.get("rake"),
                    "valley": edges.get("valley")
                },
                "faces": []
            }
            for face in (roof_gql.get("faces") or []):
                roof["faces"].append({
                    "area_sqft": face.get("area"),
                    "pitch": face.get("pitch"),
                    "azimuth": face.get("azimuth"),
                    "module_count": face.get("moduleCount")
                })

        # ── PARSE LIDAR / SHADE ───────────────────────────────
        lidar_source = gql_data.get("lidarSource") or design_rest.get("lidar_source")
        irr = gql_data.get("irradianceAnalysis") or {}
        tsrf = irr.get("tsrf")
        tof = irr.get("tof")
        annual_irradiance = irr.get("annualIrradiance")

        # ── BUILD DESIGN HISTORY ──────────────────────────────
        design_list = []
        for d in designs_list:
            did = d.get("id")
            dname = d.get("name", "?")
            system_stc_d = d.get("system_size_stc")

            design_info = {
                "name": dname,
                "milestone": d.get("milestone"),
                "system_size_kw": round(system_stc_d / 1000, 2) if system_stc_d else None,
                "production_kwh": None,
                "simulation_valid": None,
                "is_sold": did == sold_id
            }

            # Get production for each design via simple GraphQL
            if did:
                try:
                    gql_r = session.post(
                        "https://app.aurorasolar.com/graphql",
                        headers=api_headers,
                        json={"query": '{ designById(id: "' + did + '") { masterPerformanceSimulation { acPowerAnnual valid } } }'}
                    )
                    gql_d = gql_r.json()
                    s = gql_d.get("data", {}).get("designById", {}).get("masterPerformanceSimulation", {})
                    if s and s.get("acPowerAnnual"):
                        design_info["production_kwh"] = round(s["acPowerAnnual"] / 1000, 1)
                        design_info["simulation_valid"] = s.get("valid", False)
                except:
                    pass

            design_list.append(design_info)

        # ── RETURN RESULT ─────────────────────────────────────
        result = {
            "status": "ok",
            "aurora_url": f"https://v2.aurorasolar.com/projects/{project_id}",
            "project_name": project.get("name"),
            "customer": f"{project.get('customer_first_name', '')} {project.get('customer_last_name', '')}".strip(),
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
