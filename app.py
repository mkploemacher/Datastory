import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

# ---------------------------------------------------------
# 1. SETUP & CONFIGURATIE
# ---------------------------------------------------------
st.set_page_config(
    page_title="De Loonkloof in de Sport", 
    layout="wide"
)

# --- DESIGN: KLEURENPALET ---
COLOR_BG_APP = '#F0F6F8'      # Lichtblauw pastel (Achtergrond)
COLOR_ACCENT = '#E8E4D9'      # Bruinbeige pastel (Quotes/Sidebar)
COLOR_TEXT = '#0F1116'        # Donkergrijs (Hoofdtekst en Visuals text)
COLOR_GRID = '#CCCCCC'        # Duidelijkere gridkleur
COLOR_HERO_BG = '#E8E4D9'     # Bijna zwart (Titelbalk)
COLOR_HERO_TEXT = '#0F1116'   # Wit (Titelbalk tekst)

# Data Kleuren
COLOR_MEN = '#2A9D8F'         # Teal
COLOR_WOMEN = '#E76F51'       # Terra Cotta
COLOR_BROWN_LIGHT = '#A67C5B' # Warm lichtbruin
COLOR_BROWN_DARK = '#5E4B3A'  # Donker koffiebruin

# --- CSS INJECTIE ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,700;1,400&family=Playfair+Display:wght@400;700&display=swap');

    .stApp {{ background-color: {COLOR_BG_APP}; }}
    
    /* Algemene styling voor koppen */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Playfair Display', serif;
        color: {COLOR_TEXT};
        font-weight: 700;
    }}

    /* HIËRARCHIE AANPASSINGEN (Hier maken we de subkoppen kleiner) */
    h1 {{ font-size: 3rem !important; }}
    h2 {{ font-size: 2.2rem !important; }}  /* Hoofdstuktitels */
    h3 {{ font-size: 1.5rem !important; }}  /* Tussenkoppen (was te groot) */
    h4 {{ font-size: 1.2rem !important; }}  /* Kleine kopjes */
    
    p, li, div, .stMarkdown, .stCaption {{
        font-family: 'Lora', serif;
        color: {COLOR_TEXT} !important;
        font-size: 1.1rem;
        line-height: 1.7; 
    }}
    
    .block-container {{
        max-width: 900px;
        padding-top: 0rem; 
        padding-bottom: 5rem;
    }}

    /* Sidebar Styling & Links */
    section[data-testid="stSidebar"] {{ background-color: {COLOR_ACCENT}; }}
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] p {{
        font-family: 'Lora', serif;
        color: {COLOR_TEXT};
    }}
    section[data-testid="stSidebar"] a {{
        text-decoration: none;
        color: {COLOR_TEXT} !important;
        font-weight: normal;
    }}
    section[data-testid="stSidebar"] a:hover {{
        color: {COLOR_WOMEN} !important;
    }}

    /* Slider Styling (Het bolletje en de tekst) */
    div[data-testid="stSlider"] div[role="slider"] {{
        background-color: {COLOR_TEXT} !important;
        border-color: {COLOR_TEXT} !important;
        box-shadow: none !important; 
    }}
    div[data-testid="stSlider"] div[role="slider"]:active {{
        background-color: {COLOR_TEXT} !important;
    }}

    /* Hero Titelbalk */
    .hero-container {{
        background-color: {COLOR_HERO_BG};
        padding: 4rem 3rem 3rem 3rem;
        margin-top: 0;
        margin-left: -5rem;  
        margin-right: -5rem; 
        margin-bottom: 3rem;
        text-align: center;
        border-radius: 0 0 8px 8px; 
    }}
    .hero-container h1 {{ color: {COLOR_HERO_TEXT} !important; font-size: 3.5rem !important; margin-bottom: 0.5rem; }}
    .hero-container h3 {{ color: {COLOR_HERO_TEXT} !important; font-weight: 400; opacity: 0.9; font-size: 1.5rem !important; }}

    /* Quote Box */
    .quote-box {{
        background-color: {COLOR_ACCENT};
        padding: 10px 25px;
        border-left: 4px solid {COLOR_WOMEN};
        border-right: 4px solid {COLOR_WOMEN};
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 1.2rem;
        line-height: 1.3 !important;
        margin: 5px 0;
        border-radius: 4px;
        text-align: center;
    }}
    
    .footer {{
        text-align: center;
        padding: 30px;
        font-size: 0.8rem;
        color: #666;
        border-top: 1px solid #ddd;
        margin-top: 60px;
        font-family: 'Lora', serif;
    }}
    
    .stMarkdown p {{ margin-bottom: 0.5rem; }}

    /* 8. ANIMATIES (Fade-in bij laden) */
    @keyframes slideUpFade {{
        0% {{
            opacity: 0;
            transform: translateY(30px); 
        }}
        100% {{
            opacity: 1;
            transform: translateY(0);    
        }}
    }}

    .block-container {{
        animation: slideUpFade 1.2s ease-out forwards;
    }}
    
    p, h1, h2, h3, .stPlotlyChart {{
        animation: slideUpFade 1.2s ease-out forwards;
    }}
    
    .stApp {{
        overflow-x: hidden; 
    }}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DATA INLADEN
# ---------------------------------------------------------
@st.cache_data
def load_data():
    data_dict = {}
    try:
        df_top = pd.read_excel('top.xlsx')
        df_top.columns = df_top.columns.str.strip()
        if 'Earnings' in df_top.columns:
            if df_top['Earnings'].dtype == 'object':
                df_top['Earnings'] = df_top['Earnings'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
            df_top['Earnings'] = pd.to_numeric(df_top['Earnings'], errors='coerce')
        df_top['Year'] = pd.to_numeric(df_top['Year'], errors='coerce')
        data_dict['top'] = df_top
    except:
        data_dict['top'] = pd.DataFrame()
    return data_dict

data = load_data()
df_top = data['top']

# ---------------------------------------------------------
# 3. GRAFIEK FUNCTIES
# ---------------------------------------------------------
def vertaal_sport(sportnaam):
    sport_clean = str(sportnaam).lower().strip()
    vertalingen = {
        'soccer': 'Voetbal', 'basketball': 'Basketbal', 'football': 'American Football',
        'tennis': 'Tennis', 'golf': 'Golf', 'boxing': 'Boksen', 'auto racing': 'Autosport', 'f1': 'Formule 1', 'baseball': 'Honkbal'
    }
    return vertalingen.get(sport_clean, sportnaam)

def create_waffle(df_year):
    df_sorted = df_year.sort_values(by='Earnings', ascending=False).head(100).reset_index(drop=True)
    x_val, y_val, cols, txts, sizes = [], [], [], [], []
    for i in range(len(df_sorted)):
        row = i // 10
        col = i % 10
        x_val.append(col)
        y_val.append(9 - row)
        atleet = df_sorted.iloc[i]
        gender = str(atleet['Gender']).lower().strip()
        if 'female' in gender or 'women' in gender:
            cols.append(COLOR_WOMEN)
            sizes.append(24) # AANGEPAST: Iets kleiner (was 32)
        else:
            cols.append(COLOR_MEN)
            sizes.append(16) # AANGEPAST: Iets kleiner (was 22)
        txts.append(f"<b>#{i+1} {atleet['Name']}</b><br>{vertaal_sport(atleet['Sport'])}<br>${atleet['Earnings']:,.0f}")

    fig = go.Figure(data=[go.Scatter(
        x=x_val, y=y_val, mode='markers',
        marker=dict(size=sizes, color=cols, symbol='circle', line=dict(width=1, color='white')),
        text=txts, hoverinfo='text',
        textfont=dict(color=COLOR_TEXT)
    )])
    
    # Veilige dict notatie
    fig.update_layout(
        height=320, width=320, # AANGEPAST: Kleiner vierkant (was 500x500)
        plot_bgcolor=COLOR_BG_APP, paper_bgcolor=COLOR_BG_APP,
        xaxis={'visible': False, 'range': [-0.5, 9.5]}, 
        yaxis={'visible': False, 'scaleanchor': "x", 'range': [-0.5, 9.5]},
        margin={'t': 0, 'b': 0, 'l': 0, 'r': 0},
        clickmode='event+select',
        font={'family': 'Lora', 'color': COLOR_TEXT}
    )
    return fig

def create_comparison_chart():
    sporten = ['Golf', 'Tennis', 'Basketbal']
    mannen_inkomen = [1000000, 3200000, 5000000] 
    vrouwen_inkomen = [241000, 5100000, 79000]
    max_val = max(max(mannen_inkomen), max(vrouwen_inkomen))
    
    fig = go.Figure()
    
    # 1. DE STAVEN (We zetten showlegend=False, zodat we geen vierkantjes krijgen)
    fig.add_trace(go.Bar(
        name='Mannen', 
        x=sporten, 
        y=mannen_inkomen, 
        marker_color=COLOR_MEN, 
        texttemplate='$%{y:,.0f}', 
        textposition='outside',
        textfont=dict(color=COLOR_TEXT),
        showlegend=False  # Verberg het vierkantje
    ))
    
    fig.add_trace(go.Bar(
        name='Vrouwen', 
        x=sporten, 
        y=vrouwen_inkomen, 
        marker_color=COLOR_WOMEN, 
        texttemplate='$%{y:,.0f}', 
        textposition='outside',
        textfont=dict(color=COLOR_TEXT),
        showlegend=False  # Verberg het vierkantje
    ))
    
    # 2. DE LEGENDA TRUC (We voegen neppe puntjes toe voor mooie rondjes in de legenda)
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers',
        marker=dict(size=12, color=COLOR_MEN, symbol='circle'),
        name='Mannen'
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers',
        marker=dict(size=12, color=COLOR_WOMEN, symbol='circle'),
        name='Vrouwen'
    ))
    
    # 3. LAYOUT (Met expliciete zwarte titel)
    fig.update_layout(
        title={
            'text': "Mediaan Inkomen 2025",
            'font': {'color': COLOR_TEXT} # Hier dwingen we de donkere titel af
        },
        barmode='group',
        plot_bgcolor=COLOR_BG_APP, paper_bgcolor=COLOR_BG_APP,
        yaxis={'showgrid': True, 'gridcolor': COLOR_GRID, 'range': [0, max_val * 1.35], 'tickfont': {'color': COLOR_TEXT}},
        xaxis={'tickfont': {'color': COLOR_TEXT}},
        legend={'orientation': "h", 'y': 1.1, 'font': {'color': COLOR_TEXT}},
        font={'family': 'Lora', 'color': COLOR_TEXT}
    )
    return fig

def create_dumbbell_chart():
    sports = ['Basketbal', 'Golf', 'Tennis']
    men_val = [0.39, 0.14, 0.13]   
    women_val = [0.03, 0.20, 0.21] 
    fig = go.Figure()
    for i in range(len(sports)):
        fig.add_shape(type="line", x0=men_val[i], y0=sports[i], x1=women_val[i], y1=sports[i], line=dict(color="gray", width=2), layer="below")
    
    fig.add_trace(go.Scatter(x=women_val, y=sports, mode='markers+text', name='Vrouwen', marker=dict(color=COLOR_WOMEN, size=16), text=women_val, texttemplate='$%{x:.2f}', textposition='top center', textfont=dict(color=COLOR_TEXT)))
    fig.add_trace(go.Scatter(x=men_val, y=sports, mode='markers+text', name='Mannen', marker=dict(color=COLOR_MEN, size=16), text=men_val, texttemplate='$%{x:.2f}', textposition='top center', textfont=dict(color=COLOR_TEXT)))
    
    # HIER IS DE AANPASSING GEMAAKT (TITEL KLEUR)
    fig.update_layout(
        title={
            'text': "Kosten per Kijker", 
            'font': {'color': COLOR_TEXT}  # <-- Deze regel zorgt voor de donkere kleur
        }, 
        margin={'t': 50, 'b': 0, 'l': 0, 'r': 0},
        xaxis={'title': "Dollar per kijker", 'range': [0, 0.45], 'showgrid': True, 'gridcolor': COLOR_GRID, 'tickfont': {'color': COLOR_TEXT}, 'title_font': {'color': COLOR_TEXT}},
        yaxis={'showgrid': False, 'tickfont': {'color': COLOR_TEXT}}, 
        plot_bgcolor=COLOR_BG_APP, 
        paper_bgcolor=COLOR_BG_APP, 
        legend={'orientation': "v", 'y': 1, 'x': 1.05, 'font': {'color': COLOR_TEXT}}, 
        height=400,
        font={'family': 'Lora', 'color': COLOR_TEXT}
    )
    return fig

def create_line_chart_f4():
    years = [2021, 2022, 2023, 2024, 2025]
    avg_salary = [76000, 78000, 80000, 75000, 85000]
    med_salary = [74000, 74500, 75000, 75000, 75500] 
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=avg_salary, mode='lines+markers', name='Gemiddelde (Massa + Sterren)', line=dict(color=COLOR_BROWN_LIGHT, width=3)))
    fig.add_trace(go.Scatter(x=years, y=med_salary, mode='lines+markers', name='Mediaan (De massa)', line=dict(color=COLOR_BROWN_DARK, width=3, dash='dash')))
    
    fig.update_layout(
        title={
            'text': "Salarisontwikkeling WNBA (2021-2025)",
            'font': {'color': COLOR_TEXT}
        },
        plot_bgcolor=COLOR_BG_APP, paper_bgcolor=COLOR_BG_APP,
        # Y-as instellingen
        yaxis={
            'title': "Inkomen ($)", 
            'showgrid': True, 
            'gridcolor': COLOR_GRID, 
            'tickfont': {'color': COLOR_TEXT},  # Getallen y-as
            'title_font': {'color': COLOR_TEXT} # Titel y-as
        },
        # X-as instellingen (HIER ZIT DE WIJZIGING)
        xaxis={
            'tickmode': 'linear', 
            'tickfont': {'color': COLOR_TEXT}   # Getallen x-as expliciet op zwart
        },
        legend={'orientation': "h", 'y': 1.1, 'font': {'color': COLOR_TEXT}},
        font={'family': 'Lora', 'color': COLOR_TEXT}
    )
    return fig

def create_paradox_chart():
    from plotly.subplots import make_subplots
    
    fig = make_subplots(rows=1, cols=2)
    
    # Vrouwen (Linker grafiek)
    fig.add_trace(go.Bar(
        x=[-4, 35], 
        y=['Salaris', 'Kijkcijfers'],
        orientation='h',
        marker_color=COLOR_WOMEN, 
        text=[' -4%', ' +35%'], 
        textposition=['inside', 'outside'], 
        textfont=dict(color=COLOR_TEXT),
        textangle=0,       
        constraintext='none', 
        showlegend=False, 
        cliponaxis=False
    ), row=1, col=1)
    
    # Mannen (Rechter grafiek)
    fig.add_trace(go.Bar(
        x=[10, -5], 
        y=['Salaris', 'Kijkcijfers'],
        orientation='h',
        marker_color=COLOR_MEN, 
        text=[' +10%', ' -5%'], 
        textposition=['outside', 'inside'], 
        textfont=dict(color=COLOR_TEXT),
        textangle=0,       
        constraintext='none', 
        showlegend=False, 
        cliponaxis=False
    ), row=1, col=2)

    # Legenda (Grote rondjes)
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(size=16, color=COLOR_WOMEN, symbol='circle'), name='Vrouwen (WNBA)', showlegend=True), row=1, col=1)
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(size=16, color=COLOR_MEN, symbol='circle'), name='Mannen (NBA)', showlegend=True), row=1, col=1)

    # Veilige Layout update MET expliciete zwarte titel
    fig.update_layout(
        title={
            'text': "De Markt-Paradox van 2025",
            'font': {'color': COLOR_TEXT} # Hier dwingen we de donkere titel af
        },
        plot_bgcolor=COLOR_BG_APP, paper_bgcolor=COLOR_BG_APP,
        font={'family': 'Lora', 'color': COLOR_TEXT},
        margin={'l': 50, 'r': 50, 't': 50, 'b': 50},
        legend={'orientation': "v", 'y': 1, 'x': 1.05, 'font': {'color': COLOR_TEXT}}
    )
    
    # Veilige X-as update MET expliciete zwarte getallen
    common_xaxis_props = {
        'title': {'text': "% Verandering"}, 
        'range': [-19, 50], 
        'dtick': 10, 
        'tickangle': 0, 
        'zeroline': True, 
        'zerolinewidth': 2, 
        'zerolinecolor': 'white',
        'showgrid': True, 
        'gridcolor': COLOR_GRID, 
        'gridwidth': 1,
        'tickfont': {'color': COLOR_TEXT}, # Hier dwingen we de getallen op zwart
        'title_font': {'color': COLOR_TEXT}
    }

    fig.update_xaxes(**common_xaxis_props, row=1, col=1)
    fig.update_xaxes(**common_xaxis_props, row=1, col=2)
    
    # Y-as updates
    fig.update_yaxes(tickfont={'color': COLOR_TEXT}, row=1, col=1)
    fig.update_yaxes(showticklabels=False, row=1, col=2) 

    return fig
    return fig

# =========================================================
# NAVIGATION & HERO
# =========================================================
with st.sidebar:
    st.markdown("## Inhoudsopgave")
    st.markdown("""
    [1. De ongelijkheid in de top van de top](#fase1)
    
    [2. Het verschil in sportsalaris tussen man en vrouw](#fase2)
    
    [3. Is de verontwaardiging terecht?](#fase3)
    
    [4. De nuances tussen sporters en topsporters](#fase4)
    
    [5. De kloof van 134 jaar in de sport](#fase5)
 
    """)
    st.markdown("---")
    st.caption("Data Story © 2025")

st.markdown("""
<div class="hero-container">
    <h1>De emancipatie van het sportsalaris</h1>
""", unsafe_allow_html=True)

# =========================================================
# FASE 1 De ongelijkheid in de top van de top
# =========================================================

st.markdown("<div id='fase1'></div>", unsafe_allow_html=True)

st.header("De ongelijkheid in de top van de top")

st.write("""
De verdeling van salaris in de wereld blijft ongelijk. Voor een deel is dat logisch. 
Een chirurg verdient over het algemeen meer dan een monteur, maar er spelen ook factoren die minder logisch zijn. 
De loonkloof tussen mannen en vrouwen is daar één van. Het World Economic Forum berekent op basis van recente data 
dat het **134 jaar** duurt voordat de algehele gendergelijkheid volledig is bereikt *(Bron: World Economic Forum, 2024)*.
""")

col1, col2 = st.columns([2, 3]) 

# We gebruiken placeholders. Dit zijn lege vakjes die we later invullen.
# Hierdoor kunnen we de slider ONDER de grafiek zetten, maar de waarde wel gebruiken voor de tekst erboven.

with col1:
    # Reserveer plek voor de dynamische tekst (die verandert als je de slider beweegt)
    story_placeholder = st.empty()

with col2:
    # Reserveer EERST plek voor de grafiek (zodat die bovenaan staat)
    chart_placeholder = st.empty()
    
    # DAARONDER plaatsen we nu de slider
    if not df_top.empty:
        jaren = sorted(df_top['Year'].dropna().unique().astype(int))
        # Extra witruimte voor netheid
        st.write("") 
        selected_year_f1 = st.select_slider("Selecteer jaartal", options=jaren, value=2021 if 2021 in jaren else jaren[-1], label_visibility="collapsed")
        
        # Data filteren op basis van slider
        df_active = df_top[df_top['Year'] == selected_year_f1]
        fig1 = create_waffle(df_active)
        count = df_active['Gender'].astype(str).str.lower().str.contains('female|women').sum()
    else:
        selected_year_f1 = 2024
        count = 0
        fig1 = go.Figure()

    # Nu vullen we de grafiek-plek (boven de slider)
    chart_placeholder.plotly_chart(fig1, use_container_width=True)

# Als laatste vullen we de tekst links in met de juiste getallen
with story_placeholder.container():
    st.markdown("---")
    st.write(f"""
    **Stel je voor:** Je loopt binnen op één van de meest exclusieve VIP-feestjes van dit moment. 
    In de zaal staan de **100 bestbetaalde atleten ter wereld** uit het jaar **{selected_year_f1}**. 
    Je kijkt om je heen. Je ziet de allergrootste namen.
    
    **En vrouwen?** In de hele zaal met 100 multimiljonairs, staan er in {selected_year_f1} slechts **{count}**. 
    De rest staat buiten.
    """)

# Subtiele witruimte toegevoegd voor de bruine box (40px)
st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

st.markdown("""
<div class="quote-box">
“Mannen verdienen meer omdat ze harder schieten, sneller rennen en meer kijkers trekken. Dat klinkt logisch. Dat is toch hoe de markt werkt?”
</div>
""", unsafe_allow_html=True)


# =========================================================
# FASE 2: Het verschil in sportsalaris tussen man en vrouw
# =========================================================
st.markdown("<div id='fase2'></div>", unsafe_allow_html=True)
st.markdown("---")
st.header("Het verschil in sportsalaris tussen man en vrouw")

st.write("Om te begrijpen of het argument aan de borreltafel klopt, zoomen we verder in. Dit doen we door naar drie sporten te kijken die elk in een ander stadium van de emancipatiestrijd staan.")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("#### Golf")
    st.markdown("**De scheve markt.** Een individuele sport met enorme prijzen, maar waar het verschil in prijzengelden tussen mannen en vrouwen nog groot is.")

with c2:
   st.markdown("#### Tennis")
   st.markdown("**De volwassen markt.** Dankzij een lange strijd van iconen als Venus Williams en Billie Jean King is het prijzengeld op de Grand Slams nagenoeg gelijkgetrokken.")
with c3:
    st.markdown("#### Basketbal")
    st.markdown("**De groeiende markt.** Het basketbal is het strijdtoneel van nu. De NBA is een miljardenmachine, en de WNBA zit midden in een explosieve groeifase.")



 

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("### De eerste blik: Wat zegt de loonstrook?")

st.write("""
Voordat we naar de kijkcijfers gaan, kijken we eerst naar de geldcijfers.
Wat verdient de ‘middelste’ speler in 2025? Hier kiezen we voor de **mediaan** in plaats van het gemiddelde, zodat de uitschieters van de topverdieners geen vertekend beeld geven.

**De cijfers laten drie totaal verschillende beelden zien.**
""")

st.plotly_chart(create_comparison_chart(), use_container_width=True)

c_ana1, c_ana2, c_ana3 = st.columns(3)
with c_ana1:
    st.markdown("#### Golf")
    st.write("Bij Golf liggen de inkomens ver uit elkaar. De mediaan van de mannen ligt boven de \$1 miljoen, terwijl de vrouwen een mediaan van \$241.000 hebben. De mannelijke sporter verdient hier ruim 4x zoveel.")
with c_ana2:
    st.markdown("#### Tennis")
    st.write("In Tennis ligt de vergelijking anders. De mediaan van de mannen ligt op \$3,2 miljoen en die van de vrouwen op \$5,1 miljoen. Het beleid van gelijke beloning zorgt dat vrouwen dit jaar nu juist meer verdienen.")
with c_ana3:
    st.markdown("#### Basketbal")
    st.write("In het Basketbal is de kloof het grootst. De mediaan van de mannelijke speler ligt op bijna \$5 miljoen per jaar, terwijl de mediaan van de vrouwelijke speler rond \$79.000 ligt.")
    st.markdown("**Hier verdienen de mannen dus een factor 60 meer dan de vrouwen.**")

st.markdown("<br><br>", unsafe_allow_html=True)
st.write("""
**De factor 60 klinkt ontzettend groot en wellicht onrechtvaardig.** Maar in de harde wereld van de sportmarketing is ‘eerlijkheid’ een relatief begrip. 
Is deze loonkloof daarom proportioneel? 
*Als de mannen inderdaad 60 keer zoveel kijkcijfers trekken als de vrouwen, dan lijkt het verschil in de beloning perfect te verantwoorden. Maar als de kijkcijfers dichter bij elkaar liggen dan de salarissen, klopt er iets niet.*
""")

# =========================================================
# FASE 3: DE CONFRONTATIE
# =========================================================
st.markdown("---")
st.markdown("<div id='fase3'></div>", unsafe_allow_html=True)
st.header("Is de verontwaardiging terecht?")

st.write("""
**Wat is de kijker waard?**
Daarvoor berekenen we voor elke sport de meting "Kosten per Kijker." Hoeveel dollar krijgt elke speler betaald voor elke kijker? Als de markt goed werkt, zou het bedrag voor mannen en vrouwen ongeveer gelijk moeten zijn. Als dat niet zo is, is er iets anders aan de hand.
""")

st.write("""
Bij **tennis** en **golf** zien we een verrassend beeld. De **roze stip** ligt hier **rechts** van de **blauwe stip**.
* Bij tennis krijgt een vrouw gemiddeld **\$0,21** per kijker, tegenover **\$0,13** voor een man.
* Bij golf is de verhouding **\$0,20** voor vrouwen tegenover **\$0,14** voor de mannen.
""")

# HIER WORDT DE GRAFIEK GETEKEND
st.plotly_chart(create_dumbbell_chart(), use_container_width=True)
st.caption("Kosten per Kijker (Groen = Man, Oranje = Vrouw)")

st.write("""
**Wat betekent dit?** Ondanks dat mannen in absolute zin soms meer verdienen zoals bij golf, verdienen vrouwen relatief gezien meer per kijker. Het argument dat vrouwen “een lagere marktwaarde” hebben, klopt dus niet. Het relatieve salaris van de vrouwen bij tennis en golf ligt dus wel in lijn met de kijkcijfers die ze krijgen.
""")

c3_r5_c1, c3_r5_c2 = st.columns(2)
with c3_r5_c1:
    st.write("""
    **Als we dan naar basketbal kijken breekt deze logica weer.** Een mannelijke basketballer (NBA) verdient **\$0,39** voor elke kijker. Een vrouwelijke basketballer (WNBA) verdient slechts **\$0,03** per kijker.
    """)
with c3_r5_c2:
    st.write("""
    **Dat is een overwaardering van een factor 13.** De conclusie dat “mannen meer verdienen omdat ze meer kijkers trekken” bij basketbal is daarom scheef. Ze verdienen **buitenproportioneel** meer.
    """)
    
# =========================================================
# FASE 4: De nuances tussen sporters en topsporters
# =========================================================
st.markdown("<div id='fase4'></div>", unsafe_allow_html=True)
st.markdown("---")
st.header("De nuances tussen sporters en topsporters")

st.write("""
**Waarom verdienen de speelsters van Amerikaanse basketbal (WNBA) niet meer?**
Voor een mogelijke redenatie kijken we naar de geldstromen van de WNBA. Hoewel het kijkersaantal groeit, maakt de WNBA nog steeds verlies. De speelsters van de WNBA vinden dat ze eerlijker gecompenseerd moeten worden, lijkt de groei van salarissen nog uit te blijven. 
Er lijkt simpelweg “te weinig geld” te zijn voor een groei in salarissen voor de vrouwen *The Guardian* (2024). Is dit de marktwerking, of is er sprake van een systemische onderwaardering?
""")

st.markdown("<br>", unsafe_allow_html=True) 
st.markdown("""
<div class="quote-box">
"Het 'Superster-fenomeen' houdt in dat een relatief klein aantal mensen de activiteiten domineert waarin zij actief zijn en daarmee enorme hoeveelheden geld verdienen."
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True) 

# --- AANGEPASTE CAITLIN CLARK INFOBOX (NU MET RECHTER BORDER) ---
st.markdown(f"""
<div style="background-color: {COLOR_ACCENT}; padding: 20px; border-radius: 8px; border-left: 6px solid {COLOR_WOMEN}; border-right: 6px solid {COLOR_WOMEN}; margin-bottom: 25px;">
    <h4 style="margin-top: 0; color: {COLOR_TEXT};">Wie is Caitlin Clark?</h4>
    <p style="font-size: 1rem; margin-bottom: 5px;">
        Caitlin Clark (22) wordt gezien als de redder van het vrouwenbasketbal. In haar debuutjaar (2024) brak ze alle records qua kijkcijfers en stadionbezoek, een fenomeen dat in de media het <strong>"Caitlin Clark-effect"</strong> wordt genoemd. 
    </p>
    <p style="font-size: 0.9rem; margin-bottom: 0; opacity: 0.8;">
        <em>Bron: Front Office Sports (2024) & CNN (2024)</em>
    </p>
</div>
""", unsafe_allow_html=True)
# -------------------------------------------------------------

st.write("""
Het lijkt alsof het simpelweg onbetaalbaar is om de WNBA uit de rode cijfers te halen. 
Maar achter die rode cijfers schuilt het hierboven genoemde fenomeen: De **“Superster-economie.”** De recente groei in kijkcijfers kan sterk beïnvloed worden door een opkomend icoon zoals **Caitlin Clark**, die miljoenen kijkcijfers met zich mee kan trekken. 
Als supersterren de kijkcijfers zo extreem beïnvloeden, heeft dat waarschijnlijk ook invloed op de verdeling van de salarissen. 

Dit roept een belangrijke vraag op: *Vertelt het **gemiddelde** salaris wel het eerlijke verhaal, of worden we verblind door de prestaties van die paar uitzonderingen?*
""")

st.markdown("#### Waarom is dit belangrijk?")
st.write("""
In een data-analyse kan het gemiddelde een vertekend beeld geven. Een paar miljoenencontracten trekken het gemiddelde omhoog, waardoor het lijkt alsof de "gemiddelde" speelster prima verdient.
Daarom kijken we naar het verschil tussen de middelste verdienster (de **mediaan**) en het algemene gemiddelde salaris. 
Zo zien we in hoeverre topverdieners invloed hebben op het salaris van een “gewone” basketbalster.
""")

fig_f4 = create_line_chart_f4()
fig_f4.update_layout(margin=dict(b=10)) 
st.plotly_chart(fig_f4, use_container_width=True)

st.write("""
**Wat zien we in de grafiek?** De **samengestelde lijn** (gemiddelde) laat beweging zien: een dip in 2024, maar een stijging in 2025. De **gestreepte lijn** (mediaan) is nagenoeg vlak. De massa (de mediaan) blijft stabiel laag, ongeacht de hype. De 'gewone' sporter voelt nog geen verandering.
""")

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
st.subheader("De Markt-Paradox van 2025")

st.write("""
Als we dan vervolgens de kijkcijfers erbij halen en deze vergelijken met de mannelijke basketballers, stuiten we op een vreemde paradox. Zonder een causaal verband te stellen: sinds de intrede van Caitlin Clark in 2024 zijn de kijkcijfers van het vrouwenbasketbal sterk gaan groeien. 
""")

c4_r6_c1, c4_r6_c2 = st.columns([1.5, 3])
with c4_r6_c1:
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True) 
    st.write("""
    * **Bij de vrouwen (Linker grafiek):** De kijkcijfers stijgen, maar het gemiddelde salaris zakt.
    * **Bij de mannen (Rechter grafiek):** De kijkcijfers dalen, maar het salaris groeit.
    """)
with c4_r6_c2:
    st.plotly_chart(create_paradox_chart(), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
st.write("""
**Wat is nu die opvallende paradox? Het salaris van de vrouwen daalt terwijl de kijkcijfers stijgen. Mannen verdienen juist meer terwijl de kijkcijfers dalen.**
""")

st.markdown("### Wat betekent dit?")
st.write("""
Dit klinkt als slecht nieuws, maar is juist een kans. Doordat de percentuele kijkcijfers stijgen terwijl de percentuele salarissen zakken, daalt de **prijs per kijker** bij de vrouwen drastisch. 
Dat betekent dat het vrouwenbasketbal relatief snel “goedkoper” en efficiënter wordt voor adverteerders. Je bereikt miljoenen mensen voor een fractie van de prijs van het mannenbasketbal. Daarmee lijkt er een correctie-effect te ontstaan.

**Maar de data laten ook zien dat de marktwerking faalt.**
Waarom vertaalt de groei van kijkcijfers bij vrouwen zich in een krimp van het salaris, terwijl de mannen beloond worden voor krimpende kijkcijfers?

*Zit de markt op slot? Of is er simpelweg tijd nodig om oude contracten open te breken? Wanneer gaat die groei in kijkcijfers zich eindelijk vertalen in een kleinere loonkloof?*
""")

st.markdown("""
    <style>
    .element-container:last-child { margin-bottom: -50px !important; }
    </style>
    <div style='margin-bottom: -80px;'></div>
""", unsafe_allow_html=True)

# =========================================================
# FASE 5: De kloof van 134 jaar in sport
# =========================================================
st.markdown("<div id='fase5'></div>", unsafe_allow_html=True)
st.header("De kloof van 134 jaar in sport")

st.write("""
Wanneer we de mediaan van de mannen (NBA) en de vrouwen (WNBA) van 2021 tot en met 2025 naast elkaar leggen, zien we geen inhaalslag. Sterker nog, het gat wordt in absolute dollars alleen maar groter.

De salarissen van de mannen stijgen steil door, gedreven door miljardendeals uit het verleden. De salarissen van de vrouwen blijcen nagenoeg vlak op de bodem liggen. Waarom reageert de markt niet op de sterke groei van de kijkcijfers die we eerder zagen?
""")

st.write("""
Het antwoord ligt in wat economen het fenomeen **"Contractuele Vertraging"** noemen *(Basketball Reference, 2025; RunRepeat, 2025)*. De sportwereld is traag. Media-deals en spelerscontracten worden vaak voor meerdere jaren getekend. De salarissen die we **nu** in 2025 op de loonstrook zien, zijn gebaseerd op onderhandelingen uit het verleden toen het vrouwenbasketbal minder populair was. Hoewel de “Caitlin Clark revolutie” zichtbaar is op tv, zit het geld nog gevangen in oude afspraken. *Of zit er toch ook een subjectieve mannenblik achter?*
    """)

# =========================================================
# CONCLUSIE
# =========================================================
st.markdown("<div id='conclusie'></div>", unsafe_allow_html=True)
st.subheader("Conclusie")

st.write("Wat betekent dit voor de toekomst van de loonkloof? De analyse van de drie sporten laat zien dat er verschillende wegen zijn:")

c_end1, c_end2, c_end3 = st.columns(3)
with c_end1:
   st.markdown("#### Golf")
   st.caption("*De scheve markt*")
   st.write("Hier leeft nog traditie. Mannen verdienen meer, en de marktwaarde per kijker bevestigt dat de mannen hier simpelweg buitenproportioneel meer geld genereren.")
with c_end2:
   st.markdown("#### Tennis")
   st.caption("*De volwassen markt*")
   st.write("Hier is de kloof gedicht door actief beleid. Er is niet gewacht op de markt; er is besloten dat mannen en vrouwen gelijk zijn.")
with c_end3:
    st.markdown("#### Basketbal")
    st.caption("*De groeiende markt*")
    st.write("Hier faalt de markt nog op dit moment. Hoewel de vrouwen populairder zijn dan ooit, worden de salarissen van gisteren nog steeds gebruikt.")


st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")
st.write("""
We begonnen dit verhaal met een deprimerend cijfer van het World Economic Forum: In het huidige tempo duurt het nog 134 jaar voordat de algehele gendergelijkheid is bereikt. De sportwereld is een medium waar de verandering in gendergelijkheid kan plaatsvinden, zoals we bij tennis hebben gezien. Aan de andere kant zien we dat de WNBA nog steeds verlies draait, ondanks de groei in kijkcijfers. 

De vraag aan jou de lezer is daarom: **Is de sportwereld slechts een spiegel van die trage 134 jaar, of kan het de katalysator zijn die de kloof dicht?** De data laat zien dat de vrouwen recht hebben op meer. Het is geen kwestie van *of* de kloof gedicht wordt, maar *wanneer* de sportwereld de moed heeft om deze realiteit in te halen.
""")

st.write("Dat we geen genoegen moeten nemen met minder, is iets wat voorloper en tennislegende Billie Jean King decennia geleden al liet zien. Haar boodschap is glashelder:")
st.markdown("""
<div class="quote-box">
"Everyone thinks women should be thrilled when we get crumbs, and I want women to have the cake, the icing and the cherry on top too."
</div>
""", unsafe_allow_html=True)

# =========================================================
# BRONNENLIJST
# =========================================================
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("Bronnenlijst bekijken"):
    st.markdown("""
    **Geraadpleegde databronnen**
    
    * **ATP Tour.** (2024). *ATP Announces Record Social & Digital Audience Growth*. Geraadpleegd van [atptour.com](https://www.atptour.com/en/news/atp-announces-record-social-digital-audience-growth-2024) & [protennislive.com](https://www.protennislive.com/posting/ramr/current_prize.pdf).
    * **CNN.** (2024). *Sports coverage: Caitlin Clark & WNBA*. Geraadpleegd van [cnn.com](https://www.cnn.com).
    * **Concordia University, St. Paul.** (z.d.). *Infographic: Top Paid Athletes by Gender*. Kinesiology. Geraadpleegd van [kinesiology.csp.edu](https://kinesiology.csp.edu/sports-coaches-and-trainers/infographic-top-paid-athletes-by-gender/).
    * **Forbes.** (2024/2025). *NBA Viewership & Ratings Analysis*. Geraadpleegd van [forbes.com](https://www.forbes.com).
    * **Front Office Sports.** (2025). *WNBA Viewership Up Across All Networks*. Geraadpleegd van [frontofficesports.com](https://frontofficesports.com/wnba-viewership-up-across-all-networks-compared-to-2024/).
    * **Golf Monthly.** (2025). *PGA Championship TV Viewing Figures*. Geraadpleegd van [golfmonthly.com](https://www.golfmonthly.com/news/pga-championship-2025-tv-viewing-figures).
    * **LPGA.** (2020-2024). *Stats and Rankings: Money and Finishes*. Geraadpleegd van [lpga.com](https://www.lpga.com/stats-and-rankings/money-and-finishes).
    * **PlayToday.** (z.d.). *NBA Viewership Statistics*. Geraadpleegd van [playtoday.co](https://playtoday.co/blog/stats/nba-viewership-statistics/).
    * **Spotrac.** (2020-2025). *NBA, WNBA & PGA Rankings and Player Contracts*. Geraadpleegd van [spotrac.com](https://www.spotrac.com).
    * **Sports Business Journal.** (2025). *PGA Tour Viewership Bounces Back*. Geraadpleegd van [sportsbusinessjournal.com](https://www.sportsbusinessjournal.com/Articles/2025/09/02/pga-tours-viewership-bounces-back-in-big-way-from-2024s-drops/).
    * **USTVDB.** (2023-2025). *LPGA Tour Ratings (NBC & Golf Channel)*. Geraadpleegd van [ustvdb.com](https://ustvdb.com).
    * **Wikipedia.** (z.d.). *ATP & WTA Tour Overviews (2020-2024), ATP Finals & 500 Tournaments*. Geraadpleegd van [wikipedia.org](https://en.wikipedia.org).
    * **WNBA.** (2024). *WNBA Delivers Record-Setting 2024 Season*. Geraadpleegd van [wnba.com](https://www.wnba.com/news/wnba-delivers-record-setting-2024-season).
    * **World Economic Forum.** (2024). *Global Gender Gap Report 2024*. Geraadpleegd van [weforum.org](https://www.weforum.org/publications/global-gender-gap-report-2024/digest/).
    * **WTA Tennis.** (2020-2024). *Prize Money Reports & Viewership Records (1 Billion Global Audience)*. Geraadpleegd van [wtatennis.com](https://www.wtatennis.com).
    """)

st.markdown("---")
st.markdown("<div class='footer'>Data Story © 2025 • Gemaakt met Streamlit</div>", unsafe_allow_html=True)