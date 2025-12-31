import json
from core.graph_apps.pifuke.app import App

def build_context_json_str() -> str:
    payload = {
        "patientIdentity": {
            "patientId": "PID1234565",
            "idType": "01",
            "idNumber": "110101199001011235",
            "patientName": "李铁",
        },
        "visitInfo": {"department": "皮肤医美中心", "visitNumber": "V0000222"},
        "latestMedicalRecord": {
            "basicInfo": {"gender": "男", "birthday": "1985-05-20", "aboBloodType": "A", "rhBloodType": "+"},
            "vitalSigns": {"systolicPressure": 118, "diastolicPressure": 76, "height": 178, "weight": 75},
            "marriageChildInfo": {"marriageStatus": "已婚", "fullTermCount": 0, "prematureCount": 0, "abortionCount": 0, "livingChildrenCount": 0},
            "pastHistory": {
                "personalHistory": "",
                "bloodTransfusionHistory": "2015年输过2U红细胞",
                "diseaseHistory": "",
                "epidemiologicalHistory": "否认出国及接触史",
                "surgeryHistory": "无手术史",
                "familyHistory": "否认家族性遗传病、精神病、肿瘤等类似病史",
                "menstrualHistory": {"menarcheAge": 0, "intervalDays": 0, "durationDays": 0, "isSterilization": False, "lastMenstrualDate": ""},
            },
            "allergyHistory": "无",
            "childGrowthInfo": None,
        },
        "revisitInfo": {"isRevisit": 0, "lastRecord": {"chiefComplaint": "", "presentIllness": ""}},
    }
    return json.dumps(payload, ensure_ascii=False)

if __name__ == "__main__":
    app = App()
    conversation_id = "07d9fb42-d2d6-4213-8a46-69e42e42b41f"

    # =========================
    # 第一轮：输入病历上下文
    # =========================
    patient_record = build_context_json_str()
    print("=== First round: input patient record ===")

    stream_gen = app.get_response(patient_record, conversation_id, streaming=True)
    last_state = None

    for chunk in stream_gen:
        print(chunk)
        if chunk["event"] == "message_context":
            last_state = chunk["content"]

    print("\n=== FINAL STATE (after patient record) ===")
    print(last_state)

    # =========================
    # 多轮对话
    # =========================
    while True:
        user_input = input("\nYou (type 'quit' to exit): ")
        if user_input.lower() in ("quit", "exit"):
            break

        stream_gen = app.get_response(user_input, conversation_id, streaming=True)
        last_state = None
        print("\n=== New round ===")

        for chunk in stream_gen:
            print(chunk)
            if chunk["event"] == "message_context":
                last_state = chunk["content"]

        print("\n=== FINAL STATE (this round) ===")
        print(last_state)

    # =========================
    # 可选：关闭数据库连接池
    # =========================
    from extensions.ext_apps_database import connection_pool
    if connection_pool:
        connection_pool.close()
