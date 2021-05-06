# -*- coding: utf-8 -*-

"""
Yazar: Sami BABAT
Github: github.com/sam0bt/
Versiyon: 1.0
Lisans: GPL

"""

import argparse
import math
from PIL import Image

# Giriş metninin uzunluğunu saklamak için piksel sayısı.
NUM_PIXELS_TO_HIDE_LEN = 11

# 8 bitlik bir ikili sayının en önemsiz bitini çıkarmak için bir maske
MASK = 0b1


def encode(file_path, text):
    """
    Bir görüntüdeki metni kodlar. Daha spesifik olarak, metin en az anlamlı bitin içine yerleştirilmiştir
    bir görüntünün her pikselindeki her RGB değerinin. Görüntünün sağ alt 11 pikseli
    metnin uzunluğunu saklamak için ayrılmıştır.

    :param file_path: The relative path to the image. The image must be in .jpg format.
    :param text: The text to encode into the image.
    :return: An image object, containing the embedded text.
    """
    if not file_path.endswith(".jpeg") and not file_path.endswith(".jpg"):
        raise InvalidImageTypeException("Hata: Kodlanacak resim .jpg biçiminde olmalıdır")
    if not text.strip():
        raise ValueError("Giriş metni boş olmamalıdır.")

    # Kodlanacak resim
    before = Image.open(file_path)
    pixmap_before = before.load()

    '''
    Giriş metninin resme sığacağını doğrulamak için gereken piksel sayısını çıkarıyoruz
    girdi metnin boyutunu kaydedip ve ardından piksel sayısını 3 ile çarpın, çünkü 3 RGB vardır
    her pikseldeki değerler ve her girdi metninin biti, her RGB değerinin LSB'sine yerleştirilecektir.
    '''
    text_bits = tobits(text)
    num_pixels = before.size[0] * before.size[1]
    if len(text_bits) > (num_pixels - 11) * 3:
        raise ValueError("Hata: giriş metni resme sığmıyor.")

    # Resim sonucu.
    after = Image.new(before.mode, before.size)
    pixmap_after = after.load()

   # Girdi metnini resme kodlama.
    return encode_text(before, pixmap_before, after, pixmap_after, text_bits)


def encode_text(before, pixmap_before, after, pixmap_after, text_bits):
    """
    Kodlama için yardımcı işlev (dosya_yolu, metin). Bu işlev, asıl iş olan
    görüntünün her pikselindeki her RGB değerinin en önemsiz bitindeki metindir.

    :before: Resimden önce
    :pixmap_before: Önceki PIL görüntü erişim nesnesi.
    :after: Resimden Sonra.
    :pixmap_after: PIL görüntü erişim nesnesinin sonrası.
    :text_bits: Bit listesi olarak gösterilen giriş metni.
    :return: Gömülü metni içeren bir resim.
    """

    '''
    Bu, döngü sayısı tahminidir. Kod çözme işlemi gerçekleşirse bu değerin ayarlanması gerekebilir.
    işlevin son çıktıdaki son veya iki harfi eksik ise.
    '''
    num_loops = bin(int(math.ceil(len(text_bits) / 3 + 1)))
    num_loops = num_loops[2:]

   # Görüntüye girdi metninin uzunluğunu sağ alttaki ilk 11 pikselde kodlar.
    i = len(num_loops) - 1
    for x in range(NUM_PIXELS_TO_HIDE_LEN):
        r_bin, g_bin, b_bin = get_pixels_bin(pixmap_before, before.size[0] - x - 1, before.size[1] - 1)

        if i >= 0:
            b_bin = set_bit(b_bin, 0) if num_loops[i] == '1' else clear_bit(b_bin, 0)
            i -= 1
        else:
            b_bin = clear_bit(b_bin, 0)
        if i >= 0:
            g_bin = set_bit(g_bin, 0) if num_loops[i] == '1' else clear_bit(g_bin, 0)
            i -= 1
        else:
            g_bin = clear_bit(g_bin, 0)
        if i >= 0:
            r_bin = set_bit(r_bin, 0) if num_loops[i] == '1' else clear_bit(r_bin, 0)
            i -= 1
        else:
            r_bin = clear_bit(r_bin, 0)

        pixmap_after[before.size[0] - x - 1, before.size[1] - 1] = (r_bin, g_bin, b_bin)

    # Resme gerçek girdi metni kodlar.
    i = 0
    for y in range(before.size[1]):
        for x in range(before.size[0]):

            # Sağ alttaki 11 piksele metin uzunluğu verilerinin üzerine yazmaktan kaçınır.
            if y == before.size[1] - 1 and x == before.size[0] - NUM_PIXELS_TO_HIDE_LEN:
                break

            r_bin, g_bin, b_bin = get_pixels_bin(pixmap_before, x, y)
            if i < len(text_bits):
                r_bin = set_bit(r_bin, 0) if text_bits[i] == 1 else clear_bit(r_bin, 0)
                i += 1
            if i < len(text_bits):
                g_bin = set_bit(g_bin, 0) if text_bits[i] == 1 else clear_bit(g_bin, 0)
                i += 1
            if i < len(text_bits):
                b_bin = set_bit(b_bin, 0) if text_bits[i] == 1 else clear_bit(b_bin, 0)
                i += 1

            pixmap_after[x, y] = (r_bin, g_bin, b_bin)

    return after


def decode(file_path):
    """
    Gizli metin varsa, gizli metin içeren bir resmin kodunu çözer.

    :file_path: Resmin dosya yolu. Resim, .png biçiminde olmalıdır.
    :return: Resme gömülü metin. Metin yoksa boş
    string döndürülecek.
    """
    if not file_path.endswith(".png"):
        raise InvalidImageTypeException("Hata: kodu çözülecek resim .png biçiminde olmalıdır.")

    img = Image.open(file_path)
    pixmap = img.load()

    # Metnin uzunluğunu çıkarır
    bits = ''
    for x in range(NUM_PIXELS_TO_HIDE_LEN):
        r_bin, g_bin, b_bin = get_pixels_bin(pixmap, img.size[0] - x - 1, img.size[1] - 1)
        bits = str(b_bin & MASK) + bits
        bits = str(g_bin & MASK) + bits
        bits = str(r_bin & MASK) + bits

    # Resimden okunacak piksel sayısı
    loop_count = int(bits, 2)

    # Sol üst pikselden başlayarak görüntüdeki metni okur
    result = []
    index = 0
    for y in range(img.size[1]):
        for x in range(img.size[0]):

            if index == loop_count:
                break

            r_bin, g_bin, b_bin = get_pixels_bin(pixmap, x, y)
            result.append(r_bin & MASK)
            result.append(g_bin & MASK)
            result.append(b_bin & MASK)

            index += 1

    return frombits(result)


def get_pixels_bin(pixmap, x, y):
    """
    Belirtilen x ve y koordinatlarında bir piksel haritasından 3 RGB değeri döndürür. Bu değerlerin
    ikili sayılar olarak döndürülür.

    :pixmap: Bir PIL görüntü erişim nesnesi.
    :x: Pikselin x koordinatı.
    :y: Pikselin y koordinatı
    :return: İkili sayılarla temsil edilen üç RGB değeri.
    """

    r, g, b = pixmap[x, y]
    r_bin = int(bin(r), 2)
    g_bin = int(bin(g), 2)
    b_bin = int(bin(b), 2)
    return r_bin, g_bin, b_bin


def set_bit(value, bit):
    """
    'Value' içindeki tek bir biti 1 olarak ayarlar.
     value: sayı.
     bit: 1'e ayarlanacak bit.
    :return: Bitlerinden birinin value değeri 1 olarak ayarlanmış.
    """
    return value | (1 << bit)


def clear_bit(value, bit):
    """
    'Value' içindeki tek bir biti 0 olarak ayarlar.
     value: sayı.
     bit: 0'a ayarlanacak bit.
    :return: Bitlerinden birinin value değeri 0 olarak ayarlanmış.
    """
    return value & ~(1 << bit)


def tobits(s):
    """
    Bir dizeyi bit listesine dönüştürür. Giriş dizesinin UTF-8 biçiminde olması gerektiğini unutmayın.
    s: Dönüştürülecek dize.
    :return:  bit listesi.
    """
    result = []
    for c in s:
        bits = bin(ord(c))[2:]
        bits = '00000000'[len(bits):] + bits
        result.extend([int(b) for b in bits])
    return result


def frombits(bits):
    """
    Bir bit dizisini bir dizeye geri döndürür.
    bits: Dönüştürülecek bitlerin listesi.
    :return: Bitlerin tamsayı değerine sahip bir dize.
    """
    chars = []
    for b in range(int(len(bits) / 8)):
        byte = bits[b*8:(b+1)*8]
        chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
    return ''.join(chars)


# Geçersiz resim türleri için özel istisna sınıfı.
class InvalidImageTypeException(ValueError):
    def __init__(self, message):
        super().__init__(message)


# Geçersiz komut satırı argümanları için özel istisna sınıfı
class IllegalArgumentError(ValueError):
    def __init__(self, message):
        super().__init__(message)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='./SamSteg [Dosya] [-e Kodlanacak metin] [-d] [-h]')
    parser.add_argument('path', help='Kullanılacak resmin dosya yolu')
    parser.add_argument('-e', '--encode', help='Resimde kodlanacak metin')
    parser.add_argument('-d', '--decode', help='Bir resimden kod çözme', action='store_true')
    args = parser.parse_args()

    if args.encode:
        encode(args.path, args.encode).save('kodlanan.png')
    elif args.decode:
        print(decode(args.path))
