import streamlit as st
import requests
import pandas as pd
BASE_URL = "http://127.0.0.1:8000"

def insert(dataframe):
    data = dataframe.to_json(orient='split')
    response = requests.post(f"{BASE_URL}/receive", json={"data":data})
    return response

def delete_paper(paper_id):
    url = f"{BASE_URL}/papers/{paper_id}"
    response = requests.delete(url)
    return response

def show_paper(id):
    response = requests.get(f"{BASE_URL}/search_paper_id/?paper_id={id}")
    if response.status_code == 200:
        paper_data = response.json()
        df = pd.DataFrame([paper_data])
        df_paper = df
        st.dataframe(
        df_paper[["ID","title","cited_number","paper_link","cited_link","related_paper_link","snippet"]],
        column_config={"cited_number": st.column_config.NumberColumn(
                    "Citations",
                    help="Number of citations",
                    format="⭐%d",
                ),
                    "Paper_link": st.column_config.LinkColumn(
                        "paper link",
                        help="paper_link",
                        max_chars=100,
),
                    "cited_link": st.column_config.LinkColumn(
                                            "Cite papers",
                                            help="cited paper_link",
                                            max_chars=100,
                    ),
                    "related_paper_link": st.column_config.LinkColumn(
                                            "Related paper",
                                            help="related paper_link",
                                            max_chars=100,
                    )
                    
},
        hide_index=True
        )
        
        
        
    else:
        st.error("No information!")
        

def main_adm():
    st.title("Academic Paper Management System (Admin)")
    
    st.subheader("Insert")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        dataframe = pd.read_csv(uploaded_file)
        st.write(dataframe)
    if st.button("Insert"):
        info = insert(dataframe)
        st.write("Insert successfully!")

    st.subheader("Delete")
    paper_id = st.text_input("Enter the paper doi")
    if st.button("Submit"):
        if paper_id:
            show_paper(paper_id)
        else:
            st.warning("Enter the paper doi")
    
    if st.button("Delete"):
        if paper_id:
            info = delete_paper(paper_id)
            st.write("Delete successfully!")
        else:
            st.warning("Enter the paper doi to delete")

    


def main_user():
    # 标题
    st.title("Academic Paper Management System")
    search_type = st.radio("Please choose the search type", ("Author", "Paper Key Word"))
    if search_type == "Author":
        author_name = st.text_input("Enter the author name")
        if st.button("Search"):
            if author_name:
                response = requests.get(f"{BASE_URL}/search_author/?author_name={author_name}")
                if response.status_code == 200:
                    author_data = response.json()
                    print(author_data)
                    col1, col2= st.columns(2)
                    col1.metric("Author Name",author_data["author_name"])
                    col2.metric("H Index",author_data["h_index"])

                    st.write("Organization")
                    organization = ", ".join(author_data["organization"])
                    st.markdown("**"+organization+"**")

                    st.write("Research interest")
                    interest = ", ".join(author_data["interest"])
                    st.markdown("**"+interest+"**")

                    st.subheader("Paper lists")
                    

                    df = pd.DataFrame(author_data["papers"])
                    df_paper = df
                    df_paper["add"] = False 
                    st.data_editor(
                    df_paper[["add","title","cited_number","paper_link","cited_link","related_paper_link"]],
                    column_config={"cited_number": st.column_config.NumberColumn(
                                "Citations",
                                help="Number of citations",
                                format="⭐%d",
                            ),
                                "Paper_link": st.column_config.LinkColumn(
                                    "Paper link",
                                    help="paper_link",
                                    max_chars=100),
                                "cited_link": st.column_config.LinkColumn(
                                                        "Cite papers",
                                                        help="cited paper_link",
                                                        max_chars=100,
                                ),
                                "related_paper_link": st.column_config.LinkColumn(
                                                        "Related paper",
                                                        help="related paper_link",
                                                        max_chars=100,
                                ),
                                "add": st.column_config.CheckboxColumn(
                                    "Add",
                                    help="Select your **favorite** widgets",
                                    default=False
                                )
        },
                    hide_index=True,
                    disabled=["title","cited_number"]
                    )

                    
                else:
                    st.error("No information!")
            else:
                st.warning("Enter the author name")
    else:
        keyword = st.text_input("Enter the key word")
        if st.button("Search"):
            if keyword:
                response = requests.get(f"{BASE_URL}/search_paper/?title_keyword={keyword}")
                if response.status_code == 200:
                    papers_data = response.json()

                    st.subheader("Paper lists")
                    df = pd.DataFrame(papers_data["matching_papers"])
                    df_paper = df
                    df_paper["add"] = False 
                    st.data_editor(
                    df_paper[["add","title","cited_number","paper_link","cited_link","related_paper_link"]],
                    column_config={"cited_number": st.column_config.NumberColumn(
                                "Citations",
                                help="Number of citations",
                                format="⭐%d",
                            ),
                                "Paper_link": st.column_config.LinkColumn(
                                    "paper link",
                                    help="paper_link",
                                    max_chars=100,
            ),
                                "cited_link": st.column_config.LinkColumn(
                                                        "Cite papers",
                                                        help="cited paper_link",
                                                        max_chars=100,
                                ),
                                "related_paper_link": st.column_config.LinkColumn(
                                                        "Related paper",
                                                        help="related paper_link",
                                                        max_chars=100,
                                ),
                                "add": st.column_config.CheckboxColumn(
                                    "Add",
                                    help="Select your **favorite** widgets",
                                    default=False
                                )
        },
                    hide_index=True,
                    disabled=["title","cited_number","paper_link"]
                    )
                else:
                    st.error("No mathcing papers")
            else:
                st.warning("Enter the key word")



# Login and identity selection
with st.sidebar:
    st.title("Login")
    user_type = st.radio("Select user type", ("Admin", "User"))

    if user_type == "Admin":
        person = "Admin"
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            # Admin login logic
            if username == "lingyi" and password == "123456":
                st.session_state.logged_in = True
                st.success("Admin Login successful!")
            else:
                st.error("Invalid credentials")
    elif user_type == "User":
        person = "User"
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            # User login logic
            if username == "lingyi" and password == "123456":
                st.session_state.logged_in = True
                st.success("User Login successful!")
            else:
                st.error("Invalid credentials")

if st.session_state.get('logged_in', False) and person == "Admin":
    main_adm()

elif st.session_state.get('logged_in', False) and person == "User":
    main_user()