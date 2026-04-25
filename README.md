# DecryptScript

Bu repoda tek satıra obfuscate edilmiş bir Lua dosyası (`Decryptthis`) var.

## Hızlı kullanım

Aşağıdaki yardımcı script, obfuscation'ın ilk aşamasında çözülen `q` tablosunu çıkarır:

```bash
python tools/decrypt_lua_vm.py Decryptthis -o decoded_q_table.txt
```

> Not: Script'in çalışması için sistemde `lua` veya `luajit` kurulu olmalı.

## Ne işe yarar?

- `Decryptthis` içindeki başlangıç bootstrap bloğunu izole eder.
- VM gövdesi çalışmadan önce string çözümleme kısmını çalıştırır.
- Çözülen tabloyu dosyaya yazar.

Bu çıktı, kalan VM akışını manuel olarak geri okumayı ciddi şekilde kolaylaştırır.
