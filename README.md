# DecryptScript

Bu repo, obfuscate edilmiş Lua dosyasının okunabilir hale getirilmiş sürümünü içerir.

## Dosyalar

- `Decryptthis`: Orijinal (tek satır, obfuscate edilmiş) dosya.
- `Decryptthis_readable.lua`: Otomatik formatlanmış, insan tarafından okunabilir sürüm.
- `tools/make_readable_lua.py`: `Decryptthis` gibi tek satır Lua kodlarını satırlayıp girintileyen script.

## Okunabilir sürümü yeniden üretmek

```bash
python tools/make_readable_lua.py Decryptthis -o Decryptthis_readable.lua
```

## Not

Bu adım **tam VM deobfuscation** değildir; ama kodu incelemeyi mümkün kılan okunabilir bir sürüm üretir.
