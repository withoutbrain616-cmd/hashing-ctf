# Hashing Basics CTF (6 challenges)

Flask asosidagi lokal veb-CTF. 4-Lab Hashing asoslari mavzulari: SHA-256, MD5, fayl yaxlitligi, salt, rainbow table va Base64.

## Kali Linux'da ishga tushirish

```bash
cd hashing_ctf
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Brauzerda `http://127.0.0.1:5000` manzilini oching.

Agar Kali'da venv yaratishda `ensurepip` yoki `venv` xatosi chiqsa:
```bash
sudo apt update
sudo apt install python3-venv
```

## Musobaqa

- 6 ta topshiriq, har biri 100 ball; jami 600 ball.
- Jamoa nomini kiriting, topshiriqni oching, terminalda tekshirib flag yuboring.
- Reyting sahifasi natijalarni SQLite (`ctf.db`) bazasiga yozadi.
- Server standart holatda faqat `127.0.0.1` da tinglaydi. Bu lokal sinov uchun xavfsizroq.
- `debug=False` qilib ishga tushadi.

## Tashkilotchi uchun javoblar

1. `FLAG{hash_basics}`
2. `FLAG{Cyber2026!}`
3. `FLAG{integrity_ok}`
4. `FLAG{salt_changes_hash}`
5. `FLAG{admin123}` — mos parol: `admin123`
6. `FLAG{base64_is_not_encryption}`

## Eslatma

Bu o‘quv loyihasi, to‘liq ko‘p foydalanuvchili turnir platformasi emas. Hozirgi versiyada sessiya cookie orqali boshqariladi; jamoalar orasida natija yuritishda alohida brauzer/profil ishlatish tavsiya qilinadi. Uni internetga ochiq joylashtirmang.
