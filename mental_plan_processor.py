import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mental Health Plan Generator", layout="wide")

# Session state for login
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Login UI
if not st.session_state.authenticated:
    st.title("🔐 Sign In")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        if username == "admin" and password == "1234":
            st.session_state.authenticated = True
            st.success("✅ Login successful! Redirecting...")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid credentials. Try again.")

else:
    st.title("🧠 Personalized Treatment Plan Generator")

    def classify_risk(condition, glucose, bp):
        if condition == "diabetes":
            if glucose > 200:
                return "high"
            elif glucose > 140:
                return "medium"
            else:
                return "low"
        elif condition == "hypertension":
            if bp > 160:
                return "high"
            elif bp > 140:
                return "medium"
            else:
                return "low"
        return "low"

    def base_treatment_plan(condition, risk_level):
        plans = {
            "diabetes": {
                "low": ["Lifestyle changes", "Metformin (Generic)"],
                "medium": ["Metformin + Glimepiride", "Dietitian consult"],
                "high": ["Insulin therapy", "Frequent glucose monitoring"]
            },
            "hypertension": {
                "low": ["Low-salt diet", "Walking 30 mins daily"],
                "medium": ["Amlodipine (5mg)", "BP check weekly"],
                "high": ["ARBs + Beta Blockers", "Cardiology consult"]
            }
        }
        return plans.get(condition, {}).get(risk_level, ["Consult doctor"])

    def adapt_plan(plan, feedback, income, location):
        if feedback == "improved":
            return plan
        elif feedback == "no_change":
            plan.append("Add alternative medicine")
        elif feedback == "worsened":
            plan.append("Refer to specialist")
            plan.append("Increase monitoring frequency")
        return plan

    def adjust_for_resources_and_cost(plan, income, location):
        affordable = []
        for item in plan:
            if "Insulin" in item and income == "low":
                item = item.replace("Insulin", "Generic Insulin (subsidized)")
            if "consult" in item and location == "rural":
                item += " (via Telemedicine)"
            affordable.append(item)
        return affordable

    uploaded_file = st.file_uploader("📤 Upload patient CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            data = pd.read_csv(uploaded_file, encoding="utf-8-sig")
            st.success("✅ File uploaded successfully!")
            st.write("### 📊 Preview of Uploaded Data")
            st.dataframe(data.head())

            required_cols = ['id', 'condition', 'blood_glucose', 'bp_sys', 'feedback', 'income_level', 'location']
            missing = [col for col in required_cols if col not in data.columns]

            if not missing:
                st.write("### 📝 Processed Treatment Plans")
                results = []

                for _, row in data.iterrows():
                    try:
                        risk = classify_risk(row['condition'], row['blood_glucose'], row['bp_sys'])
                        plan = base_treatment_plan(row['condition'], risk)
                        adapted = adapt_plan(plan.copy(), row['feedback'], row['income_level'], row['location'])
                        final_plan = adjust_for_resources_and_cost(adapted, row['income_level'], row['location'])

                        results.append({
                            "Patient ID": row['id'],
                            "Condition": row['condition'],
                            "Risk Level": risk,
                            "Initial Plan": ", ".join(plan),
                            "Personalized Plan": ", ".join(final_plan)
                        })
                    except Exception as row_err:
                        st.warning(f"Skipping row due to error: {row_err}")

                results_df = pd.DataFrame(results)
                st.dataframe(results_df)

                csv = results_df.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Download Results as CSV", data=csv, file_name="personalized_plans.csv", mime='text/csv')
            else:
                st.error(f"❌ Missing required columns: {', '.join(missing)}")
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
    else:
        st.info("Please upload a CSV file to begin.")
