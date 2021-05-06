# SamSteg
Görüntülerdeki gizli metinleri kodlamak ve çözmek için bir steganografi aracı. PIL ve Python3 gerektirir.

## Yazar
Sami BABAT


## Çalıştırma talimatı
```bash
Kullanım: ./SamSteg [Dosya] [-e Kodlanacak metin] [-d] [-h]

Argümanlar:
  path                  Kullanılacak resmin dosya yolu

Diğer Argümanlar:
  -h, --help            Yardım mesajını görüntüler
  -e ENCODE, --encode   Resimde kodlanacak metin
  -d, --decode          Bir resimden kod çözme

```

### Resime metin gömme örneği
```python
python SamSteg.py resim.jpg -e "Kodlanan Metin"
```
### Resime gömülen metni görüntüleme örneği
```python
python SamSteg.py kodlanan.png -d
```

NOT: Kodlanan resim çalıştığınız dizine kaydedilir.

