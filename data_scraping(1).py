#!/usr/bin/env python
# coding: utf-8

# In[2]:


import requests
from bs4 import BeautifulSoup

def veri_cek(url):
    # Web sayfasını getir
    response = requests.get(url)

    # İsteğin başarılı olup olmadığını kontrol et
    if response.status_code == 200:
        # HTML içeriğini işle
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Başlık etiketini bul
        baslik_etiketi = soup.find("h1", class_="entry-title")
        baslik = baslik_etiketi.text.strip() if baslik_etiketi else "Başlık bulunamadı"

        # İçerik etiketlerini bul
        icerik_etiketleri = soup.find("div", class_="post-content entry-content")
        icerik_paragraflar = icerik_etiketleri.find_all("p") if icerik_etiketleri else []
        icerik = "\n".join([paragraf.text.strip() for paragraf in icerik_paragraflar])

        # Tüm <a> etiketlerini bul
        links = soup.find_all('a')
        link_listesi = [(link.get_text(strip=True), link.get('href')) for link in links]

        # Yorum yazarlarını bul
        yorum_yazarlari = soup.find_all("cite", class_="fn")
        yazar_listesi = [yazar.text.strip() for yazar in yorum_yazarlari]

        # Post linkini bul
        post_title_div = soup.find("div", class_="post-title")
        if post_title_div:
            a_tag = post_title_div.find("a")
            if a_tag and 'href' in a_tag.attrs:
                post_link = a_tag['href']
            else:
                post_link = "Link bulunamadı"
        else:
            post_link = "Div bulunamadı"

        # Bilgileri yazdır
        print("Başlık:", baslik)
        print("İçerik:", icerik)
        print("Linkler:")
        for link_text, link_url in link_listesi:
            print(f"Metin: {link_text}, URL: {link_url}")

        print("Yorum Yazarları:")
        for yazar in yazar_listesi:
            print(f"Yazar: {yazar}")

        print("Post Link:", post_link)

    else:
        print("Web sayfasına erişilemiyor.")

# Kullanıcıdan web sayfasının URL'sini al
url = input("Lütfen web sayfasının URL'sini girin: ")
# Veri çekme fonksiyonunu çağır
veri_cek(url)


# In[6]:


import requests
from bs4 import BeautifulSoup

def veri_cek():
    # Kullanıcıdan linki al
    link = input("Lütfen bir link girin: ")
    print()
    # Verilen linkten sayfa içeriğini çek
    response = requests.get(link)
    # HTML içeriğini BeautifulSoup ile parse et
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Başlık ve içerik etiketlerini belirle
    baslik_etiketi = soup.find("h1", class_="entry-title")
    baslik = baslik_etiketi.text.strip() if baslik_etiketi else "Başlık bulunamadı"
    
    icerik_etiketleri = soup.find("div", class_="post-content entry-content")
    icerik_paragraflar = icerik_etiketleri.find_all("p") if icerik_etiketleri else []
    icerik = "\n".join([paragraf.text.strip() for paragraf in icerik_paragraflar])

    # Link etiketlerini belirle (spesifik div içindeki linkler)
    link_etiketleri = soup.find("div", class_="tag-single small-5 medium-3 columns")
    if link_etiketleri:
        linkler = link_etiketleri.find_all("a")
        link_listesi = [(link.text.strip(), link['href']) for link in linkler]
    else:
        link_listesi = []

    # Belirli sınıfa sahip diğer linkleri ekle
    ekstra_linkler = soup.find_all("a", class_="cat-link")
    for link in ekstra_linkler:
        link_listesi.append((link.text.strip(), link['href']))
    
    # Yorum yazarlarını bul
    yorum_yazarlari = soup.find_all("cite", class_="fn")
    yazar_listesi = [yazar.text.strip() for yazar in yorum_yazarlari]
    
    # Belirli div içindeki linki al
    post_title_div = soup.find("div", class_="post-title")
    if post_title_div:
        a_tag = post_title_div.find("a")
        if a_tag and 'href' in a_tag.attrs:
            post_link = a_tag['href']
        else:
            post_link = "Link bulunamadı"
    else:
        post_link = "Div bulunamadı"
    
    # Bilgileri yazdır
    print("Başlık:", baslik)
    print()
    print("İçerik:", icerik)
    print()
    print("Linkler:")
    for link_text, link_url in link_listesi:
        print(f"Metin: {link_text}, URL: {link_url}")
    print()
    print("Yorum Yazarları:")
    for yazar in yazar_listesi:
        print(f"Yazar: {yazar}")
    print()
    print("Post Link:", post_link)

# Örnek kullanım
veri_cek()


# In[ ]:




