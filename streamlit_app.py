import streamlit as st
from app.rag import ask

st.set_page_config(
    page_title="Amazon Asistan",
    page_icon="",
    layout="centered"
)

st.title(" Amazon Müşteri Deneyimi & SSS Asistanı")
st.markdown("Merhaba! Nasıl yardımcı olabilirim?")

# Mesaj geçmişini Streamlit state'inde tutmak için
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları ekrana basma
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcıdan yeni soru alma
if prompt := st.chat_input("Amazon ile ilgili sorunuzu yazın..."):
    # Kullanıcı mesajını ekrana basıyoruz
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Asistanın cevabını üretme
    with st.chat_message("assistant"):
        with st.spinner("Bilgiler taranıyor..."):
            try:
                result = ask(prompt)
                answer = result["answer_tr"]
                
                # Ekrana cevabı yazdırma
                st.markdown(answer)

                # Kaynakları formatlı şekilde ekleme
                if result.get("sources"):
                    with st.expander("Kaynakları Gör"):
                        for source in result["sources"]:
                            st.write(f"- {source}")
                            
            except Exception as e:
                answer = "Üzgünüm, şu an cevap veremiyorum. Lütfen tekrar deneyin."
                st.error(f"Sistem Hatası: {str(e)}")

        # Asistanın cevabını geçmişe ekleme
        st.session_state.messages.append({"role": "assistant", "content": answer})  