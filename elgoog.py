import os
import re
import html
from bs4 import BeautifulSoup
import unicodedata
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import tkinter as tk
from tkinter import PhotoImage

# Diretório onde os arquivos HTML estão localizados
diretorio = 'CRPC sub-corpus oral espontÉneo'

# Lista para armazenar os documentos em texto
documentos = {}

def normalizar_palavra(palavra):
    # Normaliza a palavra (removendo a acentuação, pontuação e tornando minúsculas)
    palavra = palavra.lower()
    
    # Remove acentuação
    palavra = unicodedata.normalize('NFD', palavra).encode('ascii', 'ignore').decode('utf-8')
    
    # Remove caracteres especiais e mantém apenas letras e números
    palavra = re.sub(r'[^a-zA-Z0-9\s]', '', palavra)

    return palavra

def processar_arquivo_html(arquivo):
    with open(arquivo, "r", encoding="ISO-8859-1") as f:
        soup = BeautifulSoup(f, "html.parser")
        texto = html.unescape(soup.get_text())
        texto_normalizado = [normalizar_palavra(palavra) for palavra in texto.split()]
        texto_normalizado = " ".join(texto_normalizado)
        
        # Obtenha o nome do arquivo sem o caminho
        nome_arquivo = os.path.basename(arquivo)
        
        documentos[nome_arquivo] = texto_normalizado

# Criação do índice invertido a partir dos documentos
for raiz, subpastas, arquivos in os.walk(diretorio):
    for arquivo in arquivos:
        if arquivo.endswith((".html", ".htm")) and not arquivo.startswith("._"):
            # Processa cada arquivo HTML que não começa com "._"
            print(f"Processando arquivo: {arquivo}")
            processar_arquivo_html(os.path.join(raiz, arquivo))

# Crie um vetorizador TF-IDF
vectorizer = TfidfVectorizer()

# Aplique o vetorizador aos documentos
tfidf_matrix = vectorizer.fit_transform(documentos.values())

# Função para buscar documentos
def on_buscar():
    consulta = ''
    for campo in campos_pesquisa:
        palavra = campo.get()
        if palavra:
            consulta += f"{palavra} "

    # Transforme a consulta em uma matriz TF-IDF
    consulta_tfidf = vectorizer.transform([consulta])

    # Calcule a similaridade de cosseno entre a consulta e os documentos
    similaridades = linear_kernel(consulta_tfidf, tfidf_matrix)

    # Ordene os resultados com base na similaridade (do maior para o menor)
    resultados = list(enumerate(similaridades[0]))
    resultados = sorted(resultados, key=lambda x: x[1], reverse=True)

    lista_resultados.delete(0, tk.END)
    for resultado in resultados:
        documento_index = resultado[0]
        similaridade = resultado[1]
        
        # Se a similaridade for maior que 0, exiba o resultado
        if similaridade > 0:
            # Obtenha o nome do arquivo correspondente
            nome_arquivo = list(documentos.keys())[documento_index]
            lista_resultados.insert(tk.END, f"Arquivo: {nome_arquivo} - Similaridade: {similaridade:.2f}")

    # Exiba a quantidade de documentos encontrados
    quantidade = len([r for r in resultados if r[1] > 0])
    label_quantidade.config(text=f"Documentos encontrados: {quantidade}")

def limpar_pesquisa():
    # Remova campos de pesquisa adicionais
    for campo in campos_pesquisa:
        campo.destroy()
    campos_pesquisa.clear()

    # Limpe o resultado da pesquisa
    lista_resultados.delete(0, tk.END)
    label_quantidade.config(text="")

    # Volte ao estado inicial com um campo de pesquisa
    primeiro_campo_pesquisa = tk.Entry(frame_campos, width=20)
    primeiro_campo_pesquisa.grid(row=0, column=0, padx=10, pady=5)
    campos_pesquisa.append(primeiro_campo_pesquisa)

# Crie uma janela
janela = tk.Tk()
janela.title("Elgoog")

# Label da logo
imagem = PhotoImage(file=r"el goog.png")
                           
label_imagem = tk.Label(janela, image=imagem)
label_imagem.pack() 

# Crie um rótulo para os campos de pesquisa
label_pesquisa = tk.Label(janela, text="Campos de pesquisa:")
label_pesquisa.pack(padx=10, pady=5)

# Crie um quadro para os campos de pesquisa
frame_campos = tk.Frame(janela)
frame_campos.pack(padx=10, pady=5)

# Crie um campo de pesquisa inicial
primeiro_campo_pesquisa = tk.Entry(frame_campos, width=20)
primeiro_campo_pesquisa.grid(row=0, column=0, padx=10, pady=5)
campos_pesquisa = [primeiro_campo_pesquisa]

# Crie um botão para realizar a busca
botao_buscar = tk.Button(janela, text="Buscar", command=on_buscar)
botao_buscar.pack(padx=10, pady=5)

# Crie um botão para limpar a pesquisa
botao_limpar_pesquisa = tk.Button(janela, text="Limpar Pesquisa", command=limpar_pesquisa)
botao_limpar_pesquisa.pack(padx=10, pady=5)

# Crie uma lista para exibir os resultados
lista_resultados = tk.Listbox(janela, width=80, height=20)
lista_resultados.pack(padx=17, pady=8)

# Label para exibir a quantidade de documentos encontrados
label_quantidade = tk.Label(janela, text="")
label_quantidade.pack(padx=10, pady=5)

# Inicie a interface
janela.mainloop()
