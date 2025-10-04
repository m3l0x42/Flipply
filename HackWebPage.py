import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Flipply",
    page_icon="📦",
    layout="wide",
)



st.markdown("""
<div style="text-align:center;">
    <h1 style="color:#1f77b4;"> 📦 Flipply</h1>
    <h3>Snap the picture, get the right info, & start selling smarter!</h3>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("<h3 style='text-align:center;'> How Flippy Works</h3>", unsafe_allow_html=True)
st.markdown("""
1. Take a picture or upload an image of the item you want to sell  
2. Flipply analyzes and predicts its best selling price  
3. Post it on eBay and start selling faster and easier
""")
st.markdown("[View our GitHub Repository](https://github.com/m3l0x42/HackHarvard/tree/main) 🔗")

images = [
    "assets/hh1.jpg",
    "assets/hh2.jpg",
    "assets/hh3.jpg",
    "assets/hh4.jpg",
    "assets/hh5.jpg",
]

st.write("")
cols = st.columns(len(images))
for i, col in enumerate(cols):
    col.image(images[i], width=280)
st.markdown("---")

st.markdown("<h3 style='text-align:center;'> Watch Flipply in Action</h3>", unsafe_allow_html=True)
st.text("assets/flipply_demo.gif")

st.markdown("---")


st.markdown("<h3 style='text-align:center;'> Features</h3>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<h4 style='text-align:center;'>📸 Image Recognition</h4>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align:center;'>Snap or upload a picture - Gemini recognizes item</h6>", unsafe_allow_html=True)

with col2:
    st.markdown("<h4 style='text-align:center;'>💵 Price Prediction</h4>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align:center;'>The most balanced eBay price is predicted</h6>", unsafe_allow_html=True)

with col3:
    st.markdown("<h4 style='text-align:center;'>⚡Fast & Easy</h4>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align:center;'>Upload, predict, and sell in a matter of a quick pic</h6>", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<div style="text-align:center; margin-top:20px;">
    <h2>Want to start flipping?</h2>
    <a href="https://github.com/m3l0x42/HackHarvard/tree/main" target="_blank">
        <button style="
            background-color:#1f77b4;
            color:white;
            padding:10px 20px;
            font-size:20px;
            border:none;
            border-radius:6px;
            cursor:pointer;">Coming Soon</button>
    </a>
</div>
""", unsafe_allow_html=True)
