print("Merhaba! Ben mini AI botum 🤖")

while True:
    soru = input("Sen: ")

    if soru.lower() == "çık":
        print("AI: Görüşürüz 👋")
        break
    elif soru.lower() == "merhaba":
        print("AI: Merhaba! Nasılsın?")
    else:
        print("AI: Bunu henüz bilmiyorum 😅")