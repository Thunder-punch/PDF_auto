import os

def make_folders(base_path, company_name):
    root_path = os.path.join(base_path, company_name)
    print(f"생성할 폴더 경로: {root_path}")
    folder_list = [
        "0. 기초자료",
        os.path.join("0. 기초자료", "사무위탁"),
        os.path.join("0. 기초자료", "필요자료"),
        "1. 기초컨설팅",
        "2. 급여대장",
        "3. 지원금",
        "4. 기타"
    ]
    for folder in folder_list:
        path = os.path.join(root_path, folder)
        os.makedirs(path, exist_ok=True)
    return root_path
