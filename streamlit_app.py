import streamlit as st
import streamlit.components.v1 as components
import importlib
import app.rag
importlib.reload(app.rag)
from app.rag import ask

st.set_page_config(
    page_title="Amazon Asistan",
    page_icon="📦",
    layout="wide"
)

# Turn off Chrome translate warning by setting lang to en
components.html("<script>window.parent.document.documentElement.lang = 'tr';</script>", width=0, height=0)

# Amazon Website Clone CSS
st.markdown("""
<style>
/* 💎 Ultra Premium Modern Light UI 💎 */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Very subtle, premium background color */
.stApp {
    background-color: #F8FAFC !important;
}

/* Hide default streamlit header */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

/* Sidebar - Elegant Dark Slate Gradient */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
    border-right: none !important;
    box-shadow: 4px 0 25px rgba(0,0,0,0.1);
}

/* Sidebar Text & Selectbox */
[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}
.stSelectbox div[data-baseweb="select"] {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
}

/* Sidebar Button (Clear Chat) - Stunning Gradient Glow */
[data-testid="stSidebar"] div.stButton > button {
    background: linear-gradient(135deg, #FF9900 0%, #F59E0B 100%);
    border: none;
    border-radius: 14px;
    color: white !important;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    padding: 10px 15px;
    width: 100%;
}
[data-testid="stSidebar"] div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(245, 158, 11, 0.5);
}

/* Main Area - Popüler Sorular Buttons (Premium Cards) */
[data-testid="stMain"] div.stButton > button {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    color: #334155;
    font-weight: 500;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    padding: 14px 20px;
    margin-bottom: 8px;
    width: 100%;
}
[data-testid="stMain"] div.stButton > button:hover {
    border-color: #FF9900;
    color: #FF9900;
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(255, 153, 0, 0.12);
}

/* Chat Messages Area */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

/* User Bubble Container */
[data-testid="stChatMessage"]:nth-child(odd) {
    flex-direction: row-reverse;
}
[data-testid="stChatMessage"]:nth-child(odd) div[data-testid="chatAvatarIcon-user"] {
    display: none;
}

/* Assistant Bubble - Beautiful White Card with soft shadow */
[data-testid="stChatMessage"]:nth-child(even) .stMarkdown {
    background: #ffffff;
    border: 1px solid #f1f5f9;
    border-radius: 0 24px 24px 24px;
    padding: 1.2rem 1.8rem;
    color: #334155;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    margin-top: 15px;
    line-height: 1.6;
}

/* User Bubble - Premium Amazon Secondary Blue */
[data-testid="stChatMessage"]:nth-child(odd) .stMarkdown {
    background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
    border-radius: 24px 0 24px 24px;
    padding: 1.2rem 1.8rem;
    color: white;
    box-shadow: 0 8px 20px rgba(14, 165, 233, 0.25);
    margin-top: 15px;
    line-height: 1.6;
}

/* Chat Input Field - Floating Pill */
[data-testid="stChatInput"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 28px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.06) !important;
    padding: 5px;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #FF9900 !important;
    box-shadow: 0 10px 30px rgba(255, 153, 0, 0.15) !important;
}

/* Scrollbar styling */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
</style>
""", unsafe_allow_html=True)

# Yan menü (Sidebar) Filtreleme
with st.sidebar:
    # Amazon logosunu ve asistan ismini ortalayarak gösteriyoruz
    st.markdown("""
    <div style="text-align: center; margin-bottom: 35px; margin-top: 15px;">
        <img src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjxzdmcKICAgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogICB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIKICAgdmVyc2lvbj0iMS4xIgogICB3aWR0aD0iNjAzIgogICBoZWlnaHQ9IjE4MiIKICAgc3R5bGU9ImZpbGw6I2ZmZmZmZiIKICAgaWQ9InN2ZzE5MzYiPgogIDxwYXRoCiAgICAgZD0ibSAzNzQuMDA2NDIsMTQyLjE4NDA0IGMgLTM0Ljk5OTQ4LDI1Ljc5NzM5IC04NS43MjkwOSwzOS41NjEyMyAtMTI5LjQwNjM0LDM5LjU2MTIzIC02MS4yNDI1NSwwIC0xMTYuMzc2NTYsLTIyLjY1MTM1IC0xNTguMDg3NTcsLTYwLjMyNDk2IC0zLjI3NzEsLTIuOTYyNTIgLTAuMzQwODMsLTYuOTk5OSAzLjU5MTcxLC00LjY5MjgzIDQ1LjAxNDMxLDI2LjE5MDY0IDEwMC42NzI2OSw0MS45NDY5NyAxNTguMTY2MjMsNDEuOTQ2OTcgMzguNzc0Njg5LDAgODEuNDI5NSwtOC4wMjIzNyAxMjAuNjQ5OSwtMjQuNjcwMDYgNS45MjUwMSwtMi41MTY4MyAxMC44Nzk5OSwzLjg4MDA5IDUuMDg2MDcsOC4xNzk2NSIKICAgICBpZD0icGF0aDgiCiAgICAgc3R5bGU9ImZpbGw6I2ZmOTkwMCIgLz4KICA8cGF0aAogICAgIGQ9Im0gMzg4LjU1Njc4LDEyNS41MzYzNSBjIC00LjQ1Njg4LC01LjcxNTI3IC0yOS41NzI2MSwtMi43MDAzMyAtNDAuODQ1ODUsLTEuMzYzMjcgLTMuNDM0NDIsMC40MTk0NyAtMy45NTg3NCwtMi41NjkyNSAtMC44NjUxNywtNC43MTkwNSAyMC4wMDM0NiwtMTQuMDc4NDQgNTIuODI2OTYsLTEwLjAxNDgzIDU2LjY1NDYyLC01LjI5NTggMy44Mjc2NCw0Ljc0NTI2IC0wLjk5NjI0LDM3LjY0NzQxIC0xOS43OTM3Myw1My4zNTEyOCAtMi44ODM4NSwyLjQxMTk1IC01LjYzNjYyLDEuMTI3MzQgLTQuMzUxOTgsLTIuMDcxMTMgNC4yMjA5LC0xMC41MzkxNyAxMy42ODUxOSwtMzQuMTYwNTQgOS4yMDIxMSwtMzkuOTAyMDMiCiAgICAgaWQ9InBhdGgxMCIKICAgICBzdHlsZT0iZmlsbDojZmY5OTAwIiAvPgogIDxwYXRoCiAgICAgZD0iTSAzNDguNDk3NDQsMjAuMDY1OTggViA2LjM4MDc5IGMgMCwtMi4wNzExMyAxLjU3MzAxLC0zLjQ2MDYyIDMuNDYwNjIsLTMuNDYwNjIgaCA2MS4yNjg3NSBjIDEuOTY2MjgsMCAzLjUzOTI5LDEuNDE1NzEgMy41MzkyOSwzLjQ2MDYyIHYgMTEuNzE4OTMgYyAtMC4wMjYyLDEuOTY2MjYgLTEuNjc3ODgsNC41MzU1MSAtNC42MTQxOCw4LjU5OTEyIGwgLTMxLjc0ODU5LDQ1LjMyODkzIGMgMTEuNzk3NTksLTAuMjg4MzcgMjQuMjUwNTksMS40NjgxNCAzNC45NDcwNiw3LjQ5ODAyIDIuNDExOTUsMS4zNjMyNyAzLjA2NzM3LDMuMzU1NzUgMy4yNTA4OSw1LjMyMjAzIFYgOTkuNDUwNiBjIDAsMS45OTI0OCAtMi4yMDIyMiw0LjMyNTc2IC00LjUwOTMsMy4xMTk4IC0xOC44NDk5MiwtOS44ODM3NiAtNDMuODg3LC0xMC45NTg2NSAtNjQuNzI5MzksMC4xMDQ4NyAtMi4xMjM1NiwxLjE1MzU0IC00LjM1MTk5LC0xLjE1MzU0IC00LjM1MTk5LC0zLjE0NjAyIFYgODUuNjYwNTQgYyAwLC0yLjIyODQzIDAuMDI2MiwtNi4wMjk4OSAyLjI1NDYzLC05LjQxMTg2IGwgMzYuNzgyMjQsLTUyLjc0ODI5IGggLTMyLjAxMDc2IGMgLTEuOTY2MjYsMCAtMy41MzkyNywtMS4zODk0OCAtMy41MzkyNywtMy40MzQ0MSIKICAgICBpZD0icGF0aDEyIiAvPgogIDxwYXRoCiAgICAgZD0ibSAxMjQuOTk4ODMsMTA1LjQ1NDI0IGggLTE4LjY0MDE3IGMgLTEuNzgyNzMsLTAuMTMxMDcgLTMuMTk4NDUsLTEuNDY4MTMgLTMuMzI5NTQsLTMuMTcyMjQgViA2LjYxNjc2IGMgMCwtMS45MTM4MyAxLjU5OTIzLC0zLjQzNDQyIDMuNTkxNzEsLTMuNDM0NDIgaCAxNy4zODE3NiBjIDEuODA4OTgsMC4wNzg2IDMuMjUwODksMS40NjgxNCAzLjM4MTk5LDMuMTk4NDUgdiAxMi41MDU0NSBoIDAuMzQwODIgYyA0LjUzNTUxLC0xMi4wODU5OCAxMy4wNTU5NywtMTcuNzIyNiAyNC41Mzg5NiwtMTcuNzIyNiAxMS42NjY0OSwwIDE4Ljk1NDc3LDUuNjM2NjIgMjQuMTk4MTQsMTcuNzIyNiA0LjUwOTMsLTEyLjA4NTk4IDE0Ljc2MDA4LC0xNy43MjI2IDI1Ljc0NDk1LC0xNy43MjI2IDcuODEyNjIsMCAxNi4zNTkzMSwzLjIyNDY3IDIxLjU3NjQ2LDEwLjQ2MDUyIDUuODk4NzksOC4wNDg1NyA0LjY5MjgxLDE5Ljc0MTI4IDQuNjkyODEsMjkuOTkyMDggbCAtMC4wMjYyLDYwLjM3NzM5IGMgMCwxLjkxMzgzIC0xLjU5OTIzLDMuNDYwNjEgLTMuNTkxNzEsMy40NjA2MSBoIC0xOC42MTM5NyBjIC0xLjg2MTM4LC0wLjEzMTA3IC0zLjM1NTc0LC0xLjYyNTQzIC0zLjM1NTc0LC0zLjQ2MDYxIFYgNTEuMjkwMjUgYyAwLC00LjAzNzM5IDAuMzY3MDIsLTE0LjEwNDY2IC0wLjUyNDM0LC0xNy45MzIzMyAtMS4zODk0OSwtNi40MjMxMSAtNS41NTc5NywtOC4yMzIwOSAtMTAuOTU4NjUsLTguMjMyMDkgLTQuNTA5MywwIC05LjIyODMzLDMuMDE0OTQgLTExLjE0MjE2LDcuODM4ODUgLTEuOTEzODMsNC44MjM5IC0xLjczMDMxLDEyLjg5ODY3IC0xLjczMDMxLDE4LjMyNTU3IHYgNTAuNzAzMzggYyAwLDEuOTEzODMgLTEuNTk5MjMsMy40NjA2MSAtMy41OTE3MSwzLjQ2MDYxIGggLTE4LjYxMzk1IGMgLTEuODg3NjExLTAuMTMxMDcgLTMuMzU1NzYsLTEuNjI1NDMgLTMuMzU1NzYsLTMuNDYwNjEgTCAxNTIuOTQ2LDUxLjI5MDI1IGMgMCwtMTAuNjcwMjUgMS43NTY1MSwtMjYuMzc0MTUgLTExLjQ4Mjk4LC0yNi4zNzQxNSAtMTMuMzk2ODIsMCAtMTIuODcyNDgsMTUuMzEwNjMgLTEyLjg3MjQ4LDI2LjM3NDE1IHYgNTAuNzAzMzggYyAwLDEuOTEzODMgLTEuNTk5MjMsMy40NjA2MSAtMy41OTE3MSwzLjQ2MDYxIgogICAgIGlkPSJwYXRoMTQiIC8+CiAgPHBhdGgKICAgICBkPSJtIDQ2OS41MTQzOSwxLjE2MzY0IGMgMjcuNjU4NzcsMCA0Mi42Mjg1OCwyMy43NTI0NiA0Mi42Mjg1OCw1My45NTQyNyAwLDI5LjE3OTM0IC0xNi41NDI4NCw1Mi4zMjg4MSAtNDIuNjI4NTgsNTIuMzI4ODEgLTI3LjE2MDY2LDAgLTQxLjk0Njk3LC0yMy43NTI0NiAtNDEuOTQ2OTcsLTUzLjM1MTI3IDAsLTI5Ljc4MjM0IDE0Ljk2OTgzLC01Mi45MzE4MSA0MS45NDY5NywtNTIuOTMxODEgbSAwLjE1NzI5LDE5LjUzMTU2IGMgLTEzLjczNzYxLDAgLTE0LjYwMjc4LDE4LjcxODgxIC0xNC42MDI3OCwzMC4zODUzMiAwLDExLjY5MjcxIC0wLjE4MzUyLDM2LjY1MTE0IDE0LjQ0NTQ5LDM2LjY1MTE0IDE0LjQ0NTQ4LDAgMTUuMTI3MTIsLTIwLjEzNDUyIDE1LjEyNzEyLC0zMi40MDQwMyAwLC04LjA3NDc3IC0wLjM0MDgyLC0xNy43MjI1NyAtMi43NzksLTI1LjM3NzkgLTIuMDk3MzUsLTYuNjU5MDYgLTYuMjY1ODEsLTkuMjU0NTMgLTEyLjE5MDgzLC05LjI1NDUzIgogICAgIGlkPSJwYXRoMTYiIC8+CiAgPHBhdGgKICAgICBkPSJNIDU0OC4wMDc2MiwxMDUuNDU0MjQgSCA1MjkuNDQ2MSBjIC0xLjg2MTQxLC0wLjEzMTA3IC0zLjM1NTc3LC0xLjYyNTQzIC0zLjM1NTc3LC0zLjQ2MDYxIGwgLTAuMDI2MiwtOTUuNjkxNDkgYyAwLjE1NzMsLTEuNzU2NTMgMS43MDQxLC0zLjExOTggMy41OTE3MSwtMy4xMTk4IGggMTcuMjc2OTEgYyAxLjYyNTQzLDAuMDc4NiAyLjk2MjQ5LDEuMTc5NzYgMy4zMjk1NCwyLjY3NDEyIHYgMTQuNjI4OTkgaCAwLjM0MDggYyA1LjIxNzE3LC0xMy4wODIyIDEyLjUzMTY1LC0xOS4zMjE4MSAyNS40MDQxMiwtMTkuMzIxODEgOC4zNjMxNywwIDE2LjUxNjYyLDMuMDE0OTQgMjEuNzU5OTksMTEuMjczMjQgNC44NzYzMyw3LjY1NTMyIDQuODc2MzMsMjAuNTI3OCA0Ljg3NjMzLDI5Ljc4MjMzIHYgNjAuMjIwMTEgYyAtMC4yMDk3MywxLjY3Nzg2IC0xLjc1NjUzLDMuMDE0OTIgLTMuNTkxNjksMy4wMTQ5MiBoIC0xOC42OTI2MiBjIC0xLjcwNDExLC0wLjEzMTA3IC0zLjExOTgyLC0xLjM4OTQ4IC0zLjMwMzMyLC0zLjAxNDkyIFYgNTAuNDc3NTMgYyAwLC0xMC40NjA1MiAxLjIwNTk3LC0yNS43NzExNyAtMTEuNjY2NTEsLTI1Ljc3MTE3IC00LjUzNTUsMCAtOC43MDM5OSwzLjA0MTE3IC0xMC43NzUxMiw3LjY1NTMyIC0yLjYyMTY3LDUuODQ2MzcgLTIuOTYyNDksMTEuNjY2NTEgLTIuOTYyNDksMTguMTE1ODUgdiA1MS41MTYxIGMgLTAuMDI2MiwxLjkxMzgzIC0xLjY1MTY2LDMuNDYwNjEgLTMuNjQ0MTQsMy40NjA2MSIKICAgICBpZD0icGF0aDE4IiAvPgogIDx1c2UKICAgICB4bGluazpocmVmPSIjcGF0aDMwIgogICAgIHRyYW5zZm9ybT0idHJhbnNsYXRlKDI0NC4zNjcxOSkiCiAgICAgaWQ9InVzZTI4IiAvPgogIDxwYXRoCiAgICAgZD0iTSA1NS4yODgyNjEsNTkuNzU4MjkgViA1NS43MjA5IGMgLTEzLjQ3NTQ3MSwwIC0yNy43MTEyMTEsMi44ODM4NSAtMjcuNzExMjExLDE4Ljc3MTI1IDAsOC4wNDg1NyA0LjE2ODQ3LDEzLjUwMTY5IDExLjMyNTY3LDEzLjUwMTY5IDUuMjQzMzcsMCA5LjkzNjE4LC0zLjIyNDY3IDEyLjg5ODcsLTguNDY4MDUgMy42NzAzNDEsLTYuNDQ5MzUgMy40ODY4NDEsLTEyLjUwNTQ0IDMuNDg2ODQxLC0xOS43Njc1IG0gMTguNzk3NDcsNDUuNDMzNzggYyAtMS4yMzIxOSwxLjEwMTExIC0zLjAxNDk1LDEuMTc5NzYgLTQuNDA0NDQsMC40NDU3IC02LjE4NzE2LC01LjEzODUgLTcuMjg4MjgsLTcuNTI0MjMgLTEwLjY5NjQ3LC0xMi40MjY3OCAtMTAuMjI0NTcxLDEwLjQzNDMgLTE3LjQ2MDQwMSwxMy41NTQwOSAtMzAuNzI2MTQxLDEzLjU1NDA5IC0xNS42Nzc2OCwwIC0yNy44OTQ3MSwtOS42NzQwMSAtMjcuODk0NzEsLTI5LjA0ODI0IDAsLTE1LjEyNzEzIDguMjA1ODcsLTI1LjQzMDM1IDE5Ljg3MjM2LC0zMC40NjM5OCAxMC4xMTk3LC00LjQ1Njg4IDI0LjI1MDU4LC01LjI0MzM3IDM1LjA1MTkzMSwtNi40NzU1NiB2IC0yLjQxMTk1IGMgMCwtNC40MzA2NiAwLjM0MDgyLC05LjY3NDAzIC0yLjI1NDY1LC0xMy41MDE2NyAtMi4yODA4ODEsLTMuNDM0NDIgLTYuNjMyODYxLC00Ljg1MDEzIC0xMC40NjA1MzEsLTQuODUwMTMgLTcuMTA0NzUsMCAtMTMuNDQ5MjQsMy42NDQxNCAtMTQuOTk2MDMsMTEuMTk0NTkgLTAuMzE0NjEsMS42Nzc4OSAtMS41NDY4LDMuMzI5NTUgLTMuMjI0NjcsMy40MDgyIEwgNi4yNjI3NiwzMi42NzYyOCBDIDQuNzQyMTgsMzIuMzM1NDggMy4wNjQzLDMxLjEwMzI3IDMuNDgzNzcsMjguNzY5OTkgNy42NTIyNSw2Ljg1MjcxIDI3LjQ0NTk2LDAuMjQ2MDUgNDUuMTY4NTYsMC4yNDYwNSBjIDkuMDcxMDExLDAgMjAuOTIxMDIxLDIuNDExOTUgMjguMDc4MjIxLDkuMjgwNzYgOS4wNzEwNCw4LjQ2ODA0IDguMjA1ODcsMTkuNzY3NSA4LjIwNTg3LDMyLjA2MzIxIHYgMjkuMDQ4MjYgYyAwLDguNzMwMjIgMy42MTc5NCwxMi41NTc4NiA3LjAyNjEzLDE3LjI3NjkxIDEuMjA1OTcsMS42Nzc4NiAxLjQ2ODE0LDMuNjk2NTYgLTAuMDUyNDQsNC45NTQ5NyAtMy44MDE0NCwzLjE3MjI1IC0xMC41NjUzOCw5LjA3MTA0IC0xNC4yODgxOSwxMi4zNzQzNiBsIC0wLjA1MjQyLC0wLjA1MjUiCiAgICAgaWQ9InBhdGgzMCIgLz4KPC9zdmc+Cg==" width="110" style="margin-bottom: 15px;">
        <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 16px; font-weight: 600; color: #FF9900; letter-spacing: 0.5px; line-height: 1.4;">
            Müşteri Deneyimi<br>
            <span style="color: #ffffff; font-weight: 400; font-size: 14px;">ve SSS Asistanı</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<h2 style='font-size: 12px; font-weight: 600; color: #94a3b8; margin-bottom: -10px; text-transform: uppercase; letter-spacing: 1.5px;'>Arama Filtresi</h2>", unsafe_allow_html=True)
    
    filter_choice = st.selectbox(
        "Kategori Seçin:",
        ["Temel Sorular (SSS)", "Ürün Hakkında"],
        help="Choose whether the assistant should search the general FAQ or product reviews."
    )
    
    filter_mapping = {
        "Temel Sorular (SSS)": "faq",
        "Ürün Hakkında": "review"
    }
    selected_filter_type = filter_mapping[filter_choice]

    st.markdown("---")
    st.info("💡 **İpucu:** Kargo, iade veya hesap işlemlerini 'Temel Sorular'da; ürün performansını 'Ürün Hakkında' seçeneğiyle aratabilirsiniz.")
    
    # Sohbeti Temizle (Clear State Properly)
    if st.button("Sohbeti Temizle", use_container_width=True):
        st.session_state.messages = []
        if "example_prompt" in st.session_state:
            del st.session_state["example_prompt"]
        st.rerun()

st.markdown("""
<div style='margin-top: 20px; margin-bottom: 40px;'>
    <h1 style='font-size: 34px; font-weight: 700; color: #0F1111;'>Merhaba, ben <span style='color: #FF9900;'>Amazon AI</span> 👋</h1>
    <p style='font-size: 18px; font-weight: 400; color: #565959; margin-top: -10px;'>Size nasıl yardımcı olabilirim?</p>
</div>
""", unsafe_allow_html=True)

# Mesaj geçmişini tutmak
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sadece başlangıçta dinamik örnek soruları göster
if len(st.session_state.messages) == 0:
    category_title = "Popüler Sorular (SSS)" if selected_filter_type == "faq" else "Popüler Sorular (Ürün Hakkında)"
    st.markdown(f"<div class='section-title' style='color: #0F1111; font-weight: 600; font-size: 18px; margin-bottom: 15px;'>{category_title}</div>", unsafe_allow_html=True)
    
    if selected_filter_type == "faq":
        examples = [
            "Siparişimi nasıl takip edebilirim ve kargom nerede?",
            "Aldığım ürünü nasıl iade edebilirim? İade süresi kaç gün?",
            "Amazon Prime üyeliğinin avantajları nelerdir ve nasıl iptal edilir?",
            "İade ettiğim ürünün ücret iadesi (refund) kartıma ne zaman yansır?"
        ]
    else:
        examples = [
            "B000AO3L84 (Canon 430EX Flaş) ürününü alanlar en çok hangi özelliğini beğenmiş? Özetler misin?",
            "B000AO3L84 kodlu üründe kullanıcıların en çok şikayet ettiği kronik sorunlar neler?",
            "B000AO3L84 ürününün kutu içeriği ve temel teknik özellikleri nelerdir? Görsel de ekler misin?",
            "B000AO3L84 ASIN kodlu ürün satın alınmaya değer mi? Yorumları analiz edip bir karar ver."
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
        # Veritabanı taraması yaparken spinner göster
        with st.spinner("Lütfen bekleyin, veritabanı taranıyor..."):
            try:
                # ask() fonksiyonu sadece veritabanını tarar ve generator'ı hazırlar
                result = ask(prompt, filter_type=selected_filter_type)
            except Exception as e:
                result = None
                st.error(f"Database Error: {str(e)}")
                
        # Spinner bittikten sonra cevabı kelime kelime akıt
        if result:
            try:
                stream = result.get("answer_stream")
                
                # st.write_stream generator'ı tüketip tam stringi geri döndürür
                full_answer = st.write_stream(stream)
                
                # Hafızaya ekleme işlemini akış bittikten sonra yap
                from app.memory import add_to_memory
                add_to_memory(prompt, full_answer)

                # Yararlanılan kaynakları göster
                if result.get("sources"):
                    with st.expander("Yararlanılan Kaynakları Gör"):
                        for source in result["sources"]:
                            st.markdown(f"- `{source}`")
                            
            except Exception as e:
                full_answer = "Üzgünüm, şu an bilgiye erişemiyorum. Lütfen daha sonra tekrar deneyin."
                st.error(f"System Error: {str(e)}")

            # Asistanın tam cevabını geçmişe ekleme
            st.session_state.messages.append({"role": "assistant", "content": full_answer})