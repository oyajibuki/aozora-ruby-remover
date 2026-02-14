import streamlit as st
import re
import os
import zipfile
import io

# ===============================
# Google Analytics 設定
# ===============================
st.components.v1.html(
    """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-JBBPR56PTY"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-JBBPR56PTY');
    </script>
    """,
    height=0,
)

st.set_page_config(page_title="青空文庫 ルビ削除ツール", page_icon="📘")

st.title("📘 青空文庫 ルビ削除ツール")
st.write("txt または zip（複数txt）をアップロードしてください")

uploaded_file = st.file_uploader(
    "ファイルをアップロード",
    type=["txt", "zip"]
)

# ===============================
# ルビ削除処理
# ===============================
def remove_aozora_ruby(text: str) -> str:
    text = re.sub(r'《.*?》', '', text)
    text = re.sub(r'｜', '', text)
    text = re.sub(r'［.*?］', '', text)
    return text

def decode_text(raw: bytes) -> str:
    try:
        return raw.decode("shift_jis")
    except:
        return raw.decode("utf-8", errors="ignore")

# ===============================
# メイン処理
# ===============================
if uploaded_file and st.button("ルビを削除する"):

    # -------- txt単体 --------
    if uploaded_file.name.endswith(".txt"):
        raw = uploaded_file.read()
        content = decode_text(raw)
        result = remove_aozora_ruby(content)

        base_name = os.path.splitext(uploaded_file.name)[0]
        output_name = f"result_{base_name}.txt"

        st.download_button(
            "📄 txtでダウンロード",
            result,
            file_name=output_name,
            mime="text/plain"
        )

    # -------- zip対応 --------
    elif uploaded_file.name.endswith(".zip"):

        with zipfile.ZipFile(uploaded_file, "r") as zin:

            txt_files = [n for n in zin.namelist() if n.endswith(".txt")]

            # ---------- 1ファイルのみ ----------
            if len(txt_files) == 1:
                name = txt_files[0]
                raw = zin.read(name)
                content = decode_text(raw)
                result = remove_aozora_ruby(content)

                base = os.path.splitext(os.path.basename(name))[0]
                output_name = f"result_{base}.txt"

                # TXTダウンロード
                st.download_button(
                    "📄 txtでダウンロード",
                    result,
                    file_name=output_name,
                    mime="text/plain"
                )

                # ZIPでもDL可能
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zout:
                    zout.writestr(output_name, result)

                zip_buffer.seek(0)

                st.download_button(
                    "📦 zipでダウンロード",
                    zip_buffer,
                    file_name="result_text.zip",
                    mime="application/zip"
                )

            # ---------- 複数ファイル ----------
            else:
                zip_buffer = io.BytesIO()

                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zout:

                    for name in txt_files:
                        raw = zin.read(name)
                        content = decode_text(raw)
                        result = remove_aozora_ruby(content)

                        base = os.path.splitext(os.path.basename(name))[0]
                        out_name = f"result_{base}.txt"
                        zout.writestr(out_name, result)

                zip_buffer.seek(0)

                st.download_button(
                    "📦 zipでダウンロード",
                    zip_buffer,
                    file_name="result_texts.zip",
                    mime="application/zip"
                )
