import streamlit as st
from app.rag import ask

st.set_page_config(
    page_title="Amazon Asistan",
    page_icon="📦",
    layout="wide"
)

# Amazon Website Clone CSS
st.markdown("""
<style>
/* Font overrides to Amazon Ember */
@import url('https://fonts.googleapis.com/css2?family=Ember:wght@400;500;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Amazon Ember', Arial, sans-serif !important;
    color: #0F1111;
}

/* Hide default streamlit header */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

/* Sidebar Button (Temizle vb.) Yellow Amazon Style */
[data-testid="stSidebar"] div.stButton > button {
    background-color: #ffd814;
    border-color: #fcd200;
    border-radius: 8px;
    color: #0F1111;
    font-size: 13px;
    font-weight: 500;
    box-shadow: 0 2px 5px rgba(213,217,217,.5);
    padding: 2px 10px;
    width: 100%;
}
[data-testid="stSidebar"] div.stButton > button:hover {
    background-color: #f7ca00;
    border-color: #f2c200;
    color: #0F1111;
}

/* Main Area Buttons (Örnek Sorular Pill Style) */
[data-testid="stMain"] div.stButton > button {
    background-color: #ffffff;
    border: 1px solid #D5D9D9;
    border-radius: 100px;
    color: #0F1111;
    font-size: 14px;
    padding: 5px 15px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    margin-bottom: 5px;
}
[data-testid="stMain"] div.stButton > button:hover {
    background-color: #f7f9fa;
    border-color: #888C8C;
}

/* Chat bubble enhancements */
[data-testid="stChatMessage"] {
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    border: 1px solid #D5D9D9;
    background-color: #ffffff;
}
[data-testid="stChatMessage"]:nth-child(even) {
    background-color: #f7fafa; /* Very light blue for assistant */
    border: 1px solid #c8d8e4;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #f7f9fa;
    border-right: 1px solid #D5D9D9;
}

/* Selectbox text */
.stSelectbox label {
    font-weight: 700 !important;
    color: #0F1111 !important;
    font-size: 15px !important;
}

/* Chat Input Bar */
[data-testid="stChatInput"] {
    border-radius: 8px;
    border: 1px solid #888C8C !important;
    box-shadow: 0 1px 2px rgba(15,17,17,.15) inset;
}
[data-testid="stChatInput"]:focus-within {
    border: 1px solid #e77600 !important;
    box-shadow: 0 0 3px 2px rgba(228,121,17,.5);
}

/* Section titles */
.section-title {
    font-size: 16px;
    font-weight: 700;
    color: #0F1111;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# Yan menü (Sidebar) Filtreleme
with st.sidebar:
    # Amazon logosunu ve asistan ismini ortalayarak gösteriyoruz
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="120" style="margin-bottom: 5px;">
        <div style="font-family: 'Amazon Ember', Arial, sans-serif; font-size: 14px; font-weight: 500; color: #565959;">Müşteri Deneyimi ve SSS Asistanı</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h2 style='font-size: 16px; font-weight: 700; color: #0F1111; margin-bottom: -10px;'>Arama Filtresi</h2>", unsafe_allow_html=True)
    
    # Radio yerine daha şık duran Selectbox kullanımı
    filter_choice = st.selectbox(
        "Kategori Seçin:",
        ["Temel Sorular (SSS)", "Ürün Hakkında"],
        help="Asistanın genel müşteri hizmetleri/SSS bölümünde mi yoksa ürünlerin kendi yorumlarında mı arama yapacağını seçin."
    )

    
    # Seçime göre içerdeki filtre tipini belirle
    filter_mapping = {
        "Temel Sorular (SSS)": "faq",
        "Ürün Hakkında": "review"
    }
    selected_filter_type = filter_mapping[filter_choice]

    st.markdown("---")
    st.info("💡 **İpucu:** Kargo, iade veya hesap işlemlerini 'Temel Sorular'da; ürün performansını 'Ürün Hakkında' seçeneğiyle aratabilirsiniz.")
    
    # Sohbeti Temizle (Clear State Properly)
    if st.button("Sohbeti Temizle"):
        st.session_state.messages = []
        if "example_prompt" in st.session_state:
            del st.session_state["example_prompt"]
        st.rerun()

st.markdown("""
<h1 style='font-size: 28px; font-weight: 400; color: #0F1111; margin-bottom: 20px;'>Merhaba. Size nasıl yardımcı olabiliriz?</h1>
""", unsafe_allow_html=True)

# Mesaj geçmişini tutmak
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sadece başlangıçta dinamik örnek soruları göster
if len(st.session_state.messages) == 0:
    st.markdown("<div class='section-title'>Popüler Sorular</div>", unsafe_allow_html=True)
    
    if selected_filter_type == "faq":
        examples = [
            "Prime üyeliğin avantajları nelerdir?",
            "Aldığım bir ürünü nasıl iade edebilirim?",
            "Kargo takip işlemi nasıl yapılır?",
            "Faturamı nereden indirebilirim?"
        ]
    else:
        examples = [
            "Kullanıcılar bu ürünün malzeme kalitesi hakkında ne demiş?",
            "Bu ürünü alıp pişman olan var mı, yorumlar nasıl?",
            "Ürünün pili ne kadar dayanıyor?",
            "Fiyatına değer mi, tavsiye ediliyor mu?"
        ]
        
    cols = st.columns(2)
    for i, ex in enumerate(examples):
        with cols[i % 2]:
            if st.button(f"💬 {ex}", use_container_width=True):
                st.session_state.example_prompt = ex
                st.rerun()

# Eski mesajları ekrana basma
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcıdan yeni soru alma
prompt = st.chat_input("Yardıma ihtiyacınız olan konuyu yazın...")

# Eğer butona basılmışsa, o değeri prompt olarak al
if "example_prompt" in st.session_state:
    prompt = st.session_state.example_prompt
    del st.session_state["example_prompt"]

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Asistanın cevabı
    with st.chat_message("assistant"):
        with st.spinner("Lütfen bekleyin, veritabanı taranıyor..."):
            try:
                # Seçilen filtre tipini ask fonksiyonuna gönderiyoruz
                result = ask(prompt, filter_type=selected_filter_type)
                answer = result["answer_tr"]
                
                # Ekrana cevabı yazdırma
                st.markdown(answer)

                # Kaynakları formatlı şekilde ekleme
                if result.get("sources"):
                    with st.expander("Yararlanılan Kaynakları Gör"):
                        for source in result["sources"]:
                            st.write(f"- `{source}`")
                            
            except Exception as e:
                answer = "Üzgünüm, şu an bilgiye erişemiyorum. Lütfen daha sonra tekrar deneyin."
                st.error(f"Sistem Hatası: {str(e)}")

        # Asistanın cevabını geçmişe ekleme
        st.session_state.messages.append({"role": "assistant", "content": answer})