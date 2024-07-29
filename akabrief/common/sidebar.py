import streamlit as st


def sidebar_content(model_name):
    with st.sidebar:
        st.header("**AKABRIEF**")
        st.write(
            f"Welcome to **AKABRIEF**"
        )
        st.write(
            "AKABRIEF empowers users to effortlessly summarize documents and find answers to document-related questions."
        )

        st.markdown("Created by [Emilio Aguiar](https://www.linkedin.com/in/emilioaguiar/).")

        # Add "Star on GitHub" link to the sidebar
        badge_html = """
        <a href="https://emilio1030.github.io/ParticleGround-Portfolio/">
        <img alt="Static Badge" src="https://img.shields.io/badge/Portfolio-Python-brightgreen?logo=python">
        </a>
        """
        st.markdown(badge_html, unsafe_allow_html=True)

        st.markdown("""---""")

        st.sidebar.header("Features")
        with st.expander("⚙️ RAG Parameters"):
            st.session_state.num_source = st.slider(
                "Top N sources to view:", min_value=4, max_value=20, value=5, step=1
            )
            st.session_state.flag_mmr = st.checkbox(
                "Diversity search",
                value=True,
                help="Diversity search, i.e., Maximal Marginal Relevance (MMR) tries to reduce redundancy of fetched documents and increase diversity. 0 being the most diverse, 1 being the least diverse. 0.5 is a balanced state.",
            )
            st.session_state._lambda_mult = st.slider(
                "Diversity parameter (lambda):",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.25,
            )
            st.session_state.flag_similarity_out = st.checkbox(
                "Output similarity score",
                value=False,
                help="The retrieval process may become slower due to the cosine similarity calculations. A similarity score of 100% indicates the highest level of similarity between the query and the retrieved chunk.",
            )
