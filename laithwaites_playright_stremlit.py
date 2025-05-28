import streamlit as st
from bs4 import BeautifulSoup
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# --- HEADER ---
st.title("🍷 Wine Scraper Playwright Showcase App")
st.markdown("""
This project simulates a real-world web scraping challenge using Playwright, BeautifulSoup, and Streamlit.
""")


st.markdown("""
#### Project Overview
This project demonstrates a real-world web scraping workflow targeting a modern e-commerce site.
The wine website in question uses traditional pagination with a "next page" button to display additional results and also employs lazy loading to optimize how product images and details are loaded. After inspecting both the source code and network activity, I confirmed there is no public API or accessible static data.

To work with these constraints, I used Playwright to automate browser actions—navigating through a sample set of pages for red, white, and sparkling wine categories, and saving the resulting HTML for analysis.
Due to restrictions on Streamlit Cloud, Playwright scraping was performed offline, and the saved HTML is now used here for parsing, data extraction, and interactive analysis.

This app focuses on the crucial steps that follow scraping: turning raw HTML into usable product information, and visualizing insights for further exploration or decision making.
""")


# --- SECTION 1: Load HTML ---
st.header("1️⃣ Load Wine Data")
wine_type = st.selectbox("Choose a wine type:", ["red-wine", "white-wine", "sparkling-wine"])
if wine_type:
    selected_files = sorted(glob.glob(f"laithwaites_wines/{wine_type}_page_*.html"))
    full_html = ""
    if selected_files:
        for file in selected_files:
            with open(file, "r", encoding="utf-8") as f:
                full_html += f.read()
        st.session_state["html"] = full_html
        st.success(f"Loaded {len(selected_files)} HTML files for {wine_type.replace('-', ' ').title()}")
    else:
        st.error(f"❌ No HTML files found for {wine_type}")
        st.stop()

# --- SECTION 2: HTML Preview ---
st.header("2️⃣ Preview HTML")
if st.button("👁️ Preview Raw HTML"):
    st.text_area("HTML Preview", st.session_state["html"][:10000], height=250)
if st.button("✨ Prettify with BeautifulSoup"):
    soup = BeautifulSoup(st.session_state["html"], "html.parser")
    pretty_html = soup.prettify()
    st.text_area("Prettified HTML", pretty_html[:10000], height=250)

# --- SECTION 3: Preview Product ---
st.header("3️⃣ Preview Parsed Product")
if st.button("Preview One Product"):
    soup = BeautifulSoup(st.session_state["html"], "html.parser")
    first_product = soup.find("li", class_="ais-Hits-item")
    if first_product:
        name_tag = first_product.find("div", class_="titleDescSale")
        name = name_tag.get_text(strip=True) if name_tag else "N/A"
        link_tag = name_tag.find("a") if name_tag else None
        link = "https://www.laithwaites.co.uk" + link_tag["href"] if link_tag else "N/A"
        price_tag = first_product.find("div", class_="lowestPricepossible")
        price = price_tag.get_text(strip=True) if price_tag else "N/A"
        country_tag = first_product.find("span", class_="country-title")
        country = country_tag.get_text(strip=True) if country_tag else "N/A"
        grape_tag = first_product.find("span", class_="grapeVariety-title")
        grape = grape_tag.get_text(strip=True) if grape_tag else "N/A"
        review_tag = first_product.find("span", class_="review-count")
        reviews = review_tag.get_text(strip=True) if review_tag else "N/A"
        image_tag = first_product.find("img")
        image_url = ""
        if image_tag:
            if image_tag.has_attr("srcset"):
                srcset = image_tag["srcset"].split(",")
                largest = srcset[-1].split()[0] if srcset else image_tag["src"]
                image_url = largest
            else:
                image_url = image_tag["src"]
        st.markdown(f"""
        **Name:** [{name}]({link})  
        **Price:** {price}  
        **Country:** {country}  
        **Grape Variety:** {grape}  
        **Reviews:** {reviews}
        """)
        if image_url:
            st.image(image_url, width=50)
    else:
        st.warning("No product found in the loaded HTML.")

# --- SECTION 4: Extract All Products ---
st.header("4️⃣ Extract All Products")
st.markdown("Click to extract all products and load them into the app for analysis.")
if st.button("Extract All Products"):
    soup = BeautifulSoup(st.session_state["html"], "html.parser")
    product_cards = soup.find_all("li", class_="ais-Hits-item")
    all_products = []
    for product in product_cards:
        name_tag = product.find("div", class_="titleDescSale")
        name = name_tag.get_text(strip=True) if name_tag else "N/A"
        link_tag = name_tag.find("a") if name_tag else None
        link = "https://www.laithwaites.co.uk" + link_tag["href"] if link_tag else "N/A"
        price_tag = product.find("div", class_="lowestPricepossible")
        price = price_tag.get_text(strip=True) if price_tag else "N/A"
        country_tag = product.find("span", class_="country-title")
        country = country_tag.get_text(strip=True) if country_tag else "N/A"
        grape_tag = product.find("span", class_="grapeVariety-title")
        grape = grape_tag.get_text(strip=True) if grape_tag else "N/A"
        review_tag = product.find("span", class_="review-count")
        reviews = review_tag.get_text(strip=True) if review_tag else "N/A"
        image_tag = product.find("img")
        if image_tag:
            if image_tag.has_attr("srcset"):
                srcset = image_tag["srcset"].split(",")
                largest = srcset[-1].split()[0] if srcset else image_tag["src"]
                image_url = largest
            else:
                image_url = image_tag["src"]
        else:
            image_url = ""
        all_products.append({
            "Name": name,
            "Link": link,
            "Price": price,
            "Country": country,
            "Grape Variety": grape,
            "Reviews": reviews,
            "Image": image_url,
        })
    df = pd.DataFrame(all_products)
    st.session_state.df = df
    st.success(f"Extracted {len(df)} products!")
    st.dataframe(df)

# --- SECTION 5: Charts & Analysis ---
st.header("5️⃣ Data Visualizations")

def summer_colors(n):
    return plt.cm.summer(np.linspace(0.3, 1, n))

def get_df():
    if 'df' in st.session_state and not st.session_state.df.empty:
        return st.session_state.df
    else:
        st.error("❌ You need to click **'Extract All Products'** first to load the data.")
        st.stop()

if st.button("Show Top 7 Most Expensive Wines"):
    st.subheader("🥇 Top 7 Most Expensive Wines (per bottle)")
    df = get_df()
    df['price_num'] = df['Price'].str.replace(r"[^\d.]", "", regex=True).astype(float)
    top_expensive = df.sort_values('price_num', ascending=False).head(7)
    fig, ax = plt.subplots()
    ax.barh(top_expensive['Name'], top_expensive['price_num'], color=summer_colors(7))
    ax.set_xlabel("Price (£)")
    ax.set_ylabel("Wine Name")
    ax.invert_yaxis()
    ax.set_title("Top 7 Most Expensive Wines")
    st.pyplot(fig)

if st.button("Show Top 7 Cheapest Wines"):
    st.subheader("🥈 Top 7 Cheapest Wines (per bottle)")
    df = get_df()
    if 'price_num' not in df:
        df['price_num'] = df['Price'].str.replace(r"[^\d.]", "", regex=True).astype(float)
    top_cheap = df[df['price_num'] > 0].sort_values('price_num').head(7)
    fig, ax = plt.subplots()
    ax.barh(top_cheap['Name'], top_cheap['price_num'], color=summer_colors(7))
    ax.set_xlabel("Price (£)")
    ax.set_ylabel("Wine Name")
    ax.invert_yaxis()
    ax.set_title("Top 7 Cheapest Wines")
    st.pyplot(fig)

if st.button("Show Top 7 Most Popular Countries"):
    st.subheader("🌎 Top 7 Most Popular Countries")
    df = get_df()
    countries = df['Country'].value_counts().head(7)
    fig, ax = plt.subplots()
    ax.barh(countries.index, countries.values, color=summer_colors(7))
    ax.set_xlabel("Number of Wines")
    ax.set_ylabel("Country")
    ax.invert_yaxis()
    ax.set_title("Top 7 Most Popular Countries")
    st.pyplot(fig)

if st.button("Show Top 7 Most Popular Grape Varieties"):
    st.subheader("🍇 Top 7 Most Popular Grape Varieties")
    df = get_df()
    grapes = df['Grape Variety'].value_counts().head(7)
    fig, ax = plt.subplots()
    ax.barh(grapes.index, grapes.values, color=summer_colors(7))
    ax.set_xlabel("Number of Wines")
    ax.set_ylabel("Grape Variety")
    ax.invert_yaxis()
    ax.set_title("Top 7 Most Popular Grape Varieties")
    st.pyplot(fig)

# --- FOOTER ---
st.markdown("---")
st.info("Built with Streamlit · Scraped with Playwright · Parsed with BeautifulSoup · Visualized with Matplotlib")
