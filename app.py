import streamlit as st
from openai import OpenAI

#create OpenAI client
client= OpenAI(api_key="YOUR_API_KEY")
st.set_page_config(
     page_title="InfoLens",
     page_icon=None,
     layout="wide"
)
st.title("InfoLens")
st.markdown("""
Analyze PDFs, articles, and text from the web.
            
Upload content and extract information instantly"""
)
st.divider()
raw_text = "" #store the final extracted  text

input_type = st.radio(
      "Choose Input Type", 
      ["URL", "Text", "PDF"],
      horizontal=True
)
#  Text Input
if input_type == "Text":
      text= st.text_area("Paste text here")
      if st.button("Analyze"):
          raw_text= process_input(
               input_type= "Text",
               text= text)

# Url Input
elif input_type == "URL":
      import requests
      url= st.text_input("Enter URL")
      if url:
           st.success("URL received")
      if st.button("Analyze"):
            try:
                with st.spinner("Fetching the content"):
                     response = requests.get(url, timeout=10)
                if response.status_code!= 200:               #200 = success, 404 = Not Found, 403 = Forbidden, 500 = Server error
                  st.error(f"Could not access page. Status: {response.status_code}")
                  st.stop()
                else:
                 content_type= response.headers.get(
                      "Content-Type", 
                      ""
                 )
                 if "text/html" in content_type:
                      from bs4 import BeautifulSoup
                      soup= BeautifulSoup(
                           response.text, "html.parser")
                      raw_text= soup.get_text()
                 elif "appilcation/pdf" in content_type:
                      st.write("PDF Detected")
                 else:
                      st.error("Unsupported content type")
                raw_text= soup.get_text()
            except Exception as e:
                st.error(f"Error: {e}")

# pdf upload

elif input_type == "PDF":
      from pypdf import PdfReader

      pdf_file=st.file_uploader("Upload PDF", type= ["pdf"])
      if pdf_file:
           st.success("PDF successfully uploaded")
           st.write("File name:", pdf_file.name)
           st.write("File size:", round(pdf_file.size/1024,2), "KB")
      if st.button("Analyze") and pdf_file:
            try: 
                with st.spinner("Processing..."):
                     reader= PdfReader(pdf_file)
                raw_text= ""
                for page in reader.pages:
                     page_text= page.extract_text()
                     if page_text:
                          raw_text+= page_text + "\n"
            except Exception as e:
                st.error(f"Error: {e}")

#  Output 
          
if raw_text:
     st.divider()

     st.subheader("Extracted Text")
     st.text_area(
          "Preview", raw_text[:5000], height= 300
     )

#button
if st.button("Genrate Summary"):
     if text.strip() == "":
          st.warning("Please enter some text.")
     else:
          with st.spinner("Generating Summary..."):
               response= client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages= [
                         (
                              "role" : "user",
                              "content" : f"""
                              Summarize the following text:

                              {raw_text}
                              """
                         )
                    ]
               )
               summary= response.choices[0].message.content

          st.subheader("Summary")
          st.write(summary)