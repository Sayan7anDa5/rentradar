import streamlit as st
import pandas as pd
import joblib
from rentradar import bucket_localities

st.set_page_config(page_title="RentRadar", page_icon="🏠", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0f1419; }
    h1 { font-family: 'Space Grotesk', sans-serif !important; color: #f5f5f5 !important; font-weight: 700 !important; }
    .tagline { color: #8b9bb4; font-size: 1.05rem; margin-bottom: 2rem; }
    label { color: #c5d0e0 !important; font-weight: 500 !important; }
    .price-card {
        background: linear-gradient(135deg, #1a2332 0%, #232f45 100%);
        border: 1px solid #2d3a52; border-radius: 16px; padding: 2rem;
        text-align: center; margin-top: 1.5rem;
    }
    .price-label { color: #8b9bb4; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; }
    .price-value { font-family: 'Space Grotesk', sans-serif; color: #ffb347; font-size: 2.8rem; font-weight: 700; margin: 0.3rem 0; }
    .price-sub { color: #6b7a94; font-size: 0.8rem; }
    .stButton button {
        background-color: #ffb347; color: #0f1419; font-weight: 700;
        border: none; border-radius: 10px; padding: 0.6rem 2rem; width: 100%;
    }
    .stButton button:hover { background-color: #ffc66b; color: #0f1419; }
</style>
""", unsafe_allow_html=True)

model = joblib.load("models/rent_model.pkl")
model_columns = joblib.load("models/model_columns.pkl")
known_localities = joblib.load("models/known_localities.pkl")
clean = pd.read_csv("data/rentals_clean.csv")

st.title("🏠 RentRadar")
st.markdown('<p class="tagline">Predict a fair rent for any Indian flat — and spot a good deal.</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    city = st.selectbox("City", sorted(clean["city"].unique()))
    city_localities = sorted(clean[clean["city"] == city]["locality"].unique())
    locality = st.selectbox("Locality", city_localities)
    if locality not in known_localities:
        st.caption("ℹ️ Limited data for this locality — the estimate falls back to a broader city-level group, so changing between sparse localities won't move the price much.")
    furnishing = st.selectbox("Furnishing", sorted(clean["furnishing"].unique()))
with col2:
    beds = st.slider("Bedrooms (BHK)", 1, 4, 2)
    bathrooms = st.slider("Bathrooms", 1, 5, 2)
    area = st.number_input("Area (sq ft)", min_value=100, max_value=5000, value=800)

balconies = st.slider("Balconies", 0, 4, 1)
asking_rent = st.number_input("Asking rent (what the listing wants) ₹", min_value=1000, max_value=300000, value=25000, step=1000)

if st.button("Check This Deal"):
    input_df = pd.DataFrame([{
        "area": area, "beds": beds, "bathrooms": bathrooms,
        "balconies": balconies, "furnishing": furnishing,
        "locality": locality, "city": city
    }])
    input_df["locality"] = bucket_localities(input_df["locality"], known_localities)
    input_encoded = pd.get_dummies(input_df).reindex(columns=model_columns, fill_value=0)
    predicted = model.predict(input_encoded)[0]

    diff_pct = (asking_rent - predicted) / predicted * 100
    if diff_pct > 10:
        verdict, color, emoji = "Overpriced", "#ff6b6b", "⚠️"
    elif diff_pct < -10:
        verdict, color, emoji = "Good Deal", "#51cf66", "✅"
    else:
        verdict, color, emoji = "Fairly Priced", "#ffb347", "👍"

    st.markdown(f"""
    <div class="price-card">
        <div class="price-label">Fair Rent Estimate</div>
        <div class="price-value">₹{predicted:,.0f}</div>
        <div class="price-sub">per month · {city} · {beds} BHK · {furnishing}</div>
        <div style="margin-top:1.5rem; padding-top:1.5rem; border-top:1px solid #2d3a52;">
            <div class="price-label">Verdict on ₹{asking_rent:,.0f} asking</div>
            <div style="font-family:'Space Grotesk',sans-serif; font-size:2rem; font-weight:700; color:{color}; margin-top:0.3rem;">
                {emoji} {verdict}
            </div>
            <div class="price-sub">{abs(diff_pct):.0f}% {'above' if diff_pct > 0 else 'below'} fair estimate</div>
        </div>
    </div>
    """, unsafe_allow_html=True)