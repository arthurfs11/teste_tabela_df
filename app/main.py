import zipfile
from lxml import etree
import pandas as pd
from docx import Document

path = "files/DE_Eng_Dados_exemplo.docx"
with zipfile.ZipFile(path) as docx:
    xml = docx.read("word/document.xml")

ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
root = etree.fromstring(xml)

tabela = root.xpath('//w:tbl', namespaces=ns)[0]
linhas = tabela.xpath('.//w:tr', namespaces=ns)

linhas_mescladas = []
for i, linha in enumerate(linhas):
    for celula in linha.xpath('.//w:tc', namespaces=ns):
        merge = celula.xpath('.//w:vMerge', namespaces=ns)
        if merge and merge[0].get('{%s}val' % ns['w']) == 'continue':
            linhas_mescladas.append(i)

linhas_mescladas = [i - 1 for i in linhas_mescladas if i > 0]
doc = Document(path)
dados = []
for row in doc.tables[0].rows:
    dados.append([cell.text.strip() for cell in row.cells])

colunas = ["ID", "Fabricante", "Equipamento", "Código", "Part Number",
           "Modelo", "Descrição", "Preço Unitário", "Qtd", "Subtotal"]

df = pd.DataFrame(dados[1:], columns=colunas)
df["Subtotal"] = (df["Subtotal"]
    .str.replace("R\$|US\$|USS", "", regex=True)
    .str.replace(".", "", regex=False)
    .str.replace(",", ".", regex=False)
    .str.strip()
)
df["Subtotal_float"] = pd.to_numeric(df["Subtotal"], errors="coerce")

df_filtrado = df.drop(index=linhas_mescladas).reset_index(drop=True)
total = df_filtrado["Subtotal_float"].sum()

print(df_filtrado[[
    "ID", "Fabricante", "Equipamento", "Código", "Modelo", 
    "Descrição", "Preço Unitário", "Qtd", "Subtotal"
]])
