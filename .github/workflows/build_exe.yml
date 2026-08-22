import streamlit.web.cli as stcli
import sys
import os

if __name__ == "__main__":
    # app.py పాత్ గుర్తించడం
    base_dir = os.path.dirname(__file__)
    app_path = os.path.join(base_dir, "app.py")
    
    # streamlit run app.py కమాండ్‌ను ఇంటర్నల్‌గా రన్ చేయడం
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
        "--server.headless=false",
        "--browser.serverAddress=localhost"
    ]
    sys.exit(stcli.main())
