import streamlit as st
import re
import os
import zipfile
import io

# ===============================
# Google Analytics & GAS Counter
# ===============================
# カウンターのURL
COUNTER_URL = "https://script.google.com/macros/s/AKfycbznxYkj5ixnK_pHkGR8LUYhEYdvSYpaiF3x4LaZy964wlu068oak1X1uuIiyqCEtGWF/exec?page=aobun"

def inject_tracking():
    # 画像ではなく、Fetch APIを使ってGASからテキスト（数字）を取得して表示する方式に変更
    st.components.v1.html(
        f"""
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-JBBPR56PTY"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());
          gtag('config', 'G-JBBPR56PTY');
        </script>
        
        <!-- GAS Counter (Text Fetch) -->
        <div style="display: flex; justify-content: flex-end; align-items: center; padding-right: 10px; font-family: sans-serif;">
            <span style="font-size: 12px; color: #666; margin-right: 5px;">Access:</span>
            <span id="counter-value" style="font-size: 14px; font-weight: bold; color: #333;">...</span>
        </div>

        <script>
          fetch("{COUNTER_URL}")
            .then(response => response.text())
            .then(data => {{
              // 取得したデータがHTMLタグを含んでいる場合を考慮し、テキストのみを抽出
              const cleanData = data.replace(/<[^>]*>?/gm, '').trim();
              document.getElementById('counter-value').innerText = cleanData;
            }})
            .catch(err => {{
              console.error('Counter Error:', err);
              document.getElementById('counter-value').innerText = 'Error';
            }});
        </script>
        """,
        height=40,
    )

st.set_page_config(page_title="青空文庫 ルビ削除ツール", page_icon="📘")
inject_tracking()

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
    # ルビ（《 》）の削除
    text = re.sub(r'《.*?》', '', text)
    # ルビの開始記号（｜）の削除
    text = re.sub(r'｜', '', text)
    # 注釈（［ ］）の削除
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

        st.success(f"処理が完了しました: {uploaded_file.name}")
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

            if not txt_files:
                st.error("ZIPファイル内に .txt ファイルが見つかりませんでした。")
            
            # ---------- 1ファイルのみ ----------
            elif len(txt_files) == 1:
                name = txt_files[0]
                raw = zin.read(name)
                content = decode_text(raw)
                result = remove_aozora_ruby(content)

                base = os.path.splitext(os.path.basename(name))[0]
                output_name = f"result_{base}.txt"

                st.success(f"処理が完了しました: {name}")
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
                st.success(f"{len(txt_files)} 件のファイルを処理しました。")
                st.download_button(
                    "📦 zipでダウンロード",
                    zip_buffer,
                    file_name="result_texts.zip",
                    mime="application/zip"
                )
