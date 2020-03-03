'''
Módulo encargado del etiquetado de la extracción de estructuras para
su posterior procesamiento.

Librerias necesarias:
  
        - PDF Miner six:                https://github.com/pdfminer/pdfminer.six
            - Documentación:            https://media.readthedocs.org/pdf/pdfminer-docs/latest/pdfminer-docs.pdf 
            Utilizada para transformar PDF a texto plano a través de la función convert_pdf_to_txt
            > pip install pdfminer.six

        - Smart Pipe Library:           https://pypi.org/project/sspipe/
            Utilizada para simular el funcionamiento de una pipe y simplificar el código escrito

        - Regular Expresions Python:    https://docs.python.org/2/library/re.html 
            Utilizada para el preprocesado del texto

        - StringIO:                     https://docs.python.org/2/library/stringio.html
            Utilizada para etiquetar ficheros, se encarga de etiquetar la salida de los mismos

        - Natural Languaje Tool Kit:    http://www.nltk.org/index.html
            Utilizada para tokenizar frases y creación de bigramas y trigramas.

'''
from io import StringIO

# Simple Smart Pipe library
from sspipe import p

# RegEx library - Expresiones regulares
import re

# Natural lenguaje Tool Kit
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.util import ngrams
from collections import Counter
from unicodedata import normalize
from os.path import exists
from os import mknod


#    fichero_text_append('ficheros_salida/salida_ConteoBigramas.txt', "Fin del top 100 ---") 
def append_text_file(path,text):
    '''
        :param path:    String no vacio relativo a la ruta donde se generará el output
        :param text:    String a guardar en el fichero
        :return:        Añade al final del archivo en la ruta "path" el string "text"
    '''

    file = open(path,'a+')
    file.write(text)
    file.close()
    return 1





def create_text_file(path,text):
    '''
        :param path:    String no vacio relativo a la ruta donde se generará el output
        :param text:    String a guardar en el fichero
        :return:        Genera un fichero de texto en el directorio path cuyo contenido
                         es text
    '''
    file = open(path,'w+')
    file.write(text)
    file.close()
    return 1






def delete_jumps(text):
    '''
        :param text:        String a procesar.
        :return:            A través de una expresión regular eliminar los saltos de línea
                            la letra final seguida de un salto de linea y 
                            comenzando por otra letra minúscula.     
    '''
    p1 = re.compile(r'((\w|, |\)) *)\n+([a-z]|\(|\¿|\")', re.MULTILINE | re.DOTALL |re.UNICODE)
    text2 = p1.sub(r'\1\3',text)
    return text2






def delete_whitespaces(text):
    '''
        :param text:            String a procesar.
        :return:               	Identifica dos espacios (carácter 32 en ASCII) y
        						sustituyéndolos por uno solo. 
    '''
    p1 = re.compile(r' {2,}',re.UNICODE)
    text2 = p1.sub(r' ',text)
    return text2






def label_ordered_lists(text):
    '''
    ..  note:: 
        Ejemplo de listas ordenadas: 	
            - 1. Texto1
            - 2. Texto2
            - 3. Texto3

    :param text:	String a procesar
    :return:        Identifica un número seguido de punto y el texto consiguiente.
                    Tras ello, busca que exista otra estructura similar en la siguiente
                    línea.
    '''
    p1 = re.compile(r'( *[0-9]+\. .+\n( *[0-9]+\. .+\n)+)\n+(\w)',re.UNICODE)
    text2 = p1.sub(r'<ol>\n\1<\\ol>\n\3',text)

    return text2
 





def label_h1(text):
    '''
    .. note::
	    Título:
		    - 1.		Título de primer nivel
		    - 1.1.	    Título de segundo nivel
		    - 1.1.1.	Título de tercer nivel

    :param text:	String a procesar
    :return:       	Identifica una estructura de título. Tras ello, etiqueta el apartado con
                las etiquetas <h1..n> Título1 <\h1..n>
    '''
    p1 = re.compile(r'(\n[0-9]\. .+\n)', re.MULTILINE|re.UNICODE) 
    text2 = p1.sub(r'\n\n<h1>\1<\\h1>\n\n',text)

    return text2




def label_h2(text):
    p1 = re.compile(r'(\n *[0-9]\.[0-9]\. .+\n)',re.MULTILINE|re.UNICODE) 
    text2 = p1.sub(r'\n\n<h2>\1<\\h2>\n\n',text)

    return text2




def label_h3(text):
    p1 = re.compile(r'(\n *[0-9]\.[0-9]\.[0-9]\. .+\n)',re.MULTILINE|re.UNICODE) 
    text2 = p1.sub(r'\n\n<h3>\1<\\h3>\n\n',text)

    return text2




def label_h4(text):
    p1 = re.compile(r'(\n *[0-9]\.[0-9]\.[0-9]\.[0-9]\. .+\n)',re.MULTILINE|re.UNICODE) 
    text2 = p1.sub(r'\n\n<h4>\1<\\h4>\n\n',text)

    return text2



def label_headers(text):
    ''' 
  	    :return: etiqueta todos los niveles de títulos
    '''
    texto_procesado = ( label_h1(text)      | p(label_h2)
                                            | p(label_h3)
                                            | p(label_h4)
    )
    return texto_procesado





def fit_titles(text):
    '''
        :param text:        String a procesar
        :return:            Ajusta títulos
    '''
    p1 = re.compile(r'([^<li>]+) *\n{2,}(<li>.+\n+)',re.UNICODE) 
    text2 = p1.sub(r'\1\n\2',text)

    return text2





def delete_dash(text):
    '''
        :param text:        String a procesar
        :return:            Identifica un los guiones al final de una palabra en línea y lo une 
                            a su continuación de la línea siguiente
    '''
    

    texto = text.replace(chr(10),"<line>")
    p1 = re.compile(r'([a-záéíóú])-(<line>)+(\d+)(<line>)+([a-záéíóú]*)') 
    text2 = p1.sub(r'\1\5 <page n=\3> ',texto)
    p = re.compile(r'([a-z])-(<line>)+([a-z])', re.UNICODE)
    text3 = p.sub(r'\1\3',text2)

        
    text4 = re.sub(r'([a-záéíóú])-(<line>)+([a-záéíó])',r'\1\3',text3,re.UNICODE)
    p = re.compile(r'(<line> *([0-9]*\.)+ *[^<]+)', re.UNICODE)
    text5 = p.sub(r'\n\1',text4)
  
    text6 = text5.replace("<line><line>", chr(10)+chr(10))

    text7 = text6.replace("<line><li>", chr(10)+"<li>")
    text8 = text7.replace("<line>", " ")
    return text8





def delete_false_headers(text):
    '''
        :return:    Elimina caracteres equívocos en headers del texto
    '''
    return text.replace(chr(61602),'\n')





def delete_0C(text):
    '''
        :return:    Elimina el ASCII 0C situado en al final de página para evitar errores
    '''
    texto = text.replace(chr(12),'')
    texto = texto.replace(chr(169),'')
    texto = texto.replace(chr(10),'\n')

    return texto





def delete_CID(text):
    '''
        :return:    Sustituye símbolos no identificados en etiquetado en listas no ordenadas
                    por su etiqueta correspondiente "<li>" además gestiona letras incorrectamente
                    extraidas por la etiqueta de formato CID
    '''
    p1 = re.compile(r'(\(cid:114\) *)') 
    text2 = p1.sub(r'<li>',text)
    p2 = re.compile(r'(\(cid:([0-9]+)\) *)', re.MULTILINE | re.DOTALL |re.UNICODE)
    text3 = p2.sub(lambda m: chr(int(m.group(2))+31),text2)

    # Gestion incorrecta de letras
    text3.replace(chr(229),"a")   
    text3.replace(chr(245),"o") 
    text3.replace(chr(10),"o") 
    text3.replace(chr(245),"o") 
    text3.replace(chr(240),"o") 
    text3.replace(chr(251),"u") 
     
    return text3





def correct_labeling(text):
    '''
    ..note::
        - Inicial:
            <li>
                texto de ejemplo
        - Final:
            <li> texto de ejemplo
    :return:    Corrige una etiqueta <li>\n seguida del texto
    '''
    p2 = re.compile(r'(<li>\s* *.*)\n{1,2}([a-z])', re.MULTILINE | re.DOTALL |re.UNICODE)
    text2 = p2.sub(r'\1 \2',text)
 
    return text2





def delete_listCHR(text):
    
    '''
    .. note::
        Ejemplo de texto ordenado con el carácter 1F
            - Texto1
            - Texto2
            - Texto3
    :return:     Elimina los caracteres propios de la inclusión de viñetas
                a la hora de ordenar texto:       
    '''
    texto = text.replace(chr(31),"<li>")
    texto = texto.replace(chr(61613),"<li>")
    texto = texto.replace(chr(61550),"<li>")
    texto = texto.replace(chr(8226),"<li>")
    texto = texto.replace(chr(8212),"<li>")
    texto = texto.replace(chr(61623),"<li>")
    texto = texto.replace(chr(61680),"<li>")

    return texto





def delete_emptyListCHR(text):
    '''
    :return:    Elimina los caracteres de lista no ordenada de un texto y los <li> que se encuentran dentro de palabras
    '''

    p1 = re.compile(r'\n+<li>\s+\n+', re.UNICODE)
    text2 = p1.sub(r'',text)
    p2 = re.compile(r'(\w)<li>(\w)', re.UNICODE)
    text3 = p2.sub(r'\1\2',text2)

    return text3





def delete_list_jumps(text):
    '''
    :return:    Elimina las palabras inacabadas con saltos de línea, juntando
                el final de línea y palabra con su continuación.
    '''
    p1 = re.compile(r'(<li> [^-\n]+)[' '*\n|\-' '*\n]\n+([a-z].+\.)', re.UNICODE)
    text2 = p1.sub(r'\1\2> ',text)

    return text2





def delete_list_doublejumps(text):
    '''
    :return:    Elimina los saltos de línea dobles en guías clínicas
    '''

    p1 = re.compile(r'(<li>\s* *.+)\n\n([a-z])', re.UNICODE)
    text2 = p1.sub(r'\1\2> ',text)
    return text2





def delete_double_jump_start(text):
    '''
    :return:    Elimina los saltos de línea entre la úlima frase antes de una etiqueta <li>
                y la propia etiqueta
    .. note::
        Ejemplo de salto de línea previo a una etiqueta
            - Texto1
            - Texto2
            - Texto3
     
    '''
    p1 = re.compile(r'(.+)\n{2,}( *<li> .+\.)', re.UNICODE)
    text2 = p1.sub(r'\1\n\2> ',text)

    return text2





def delete_double_endline_list(text):

    ''' 
    :return:    Elimina los dobles saltos de línea entre una misma lista
                palabras no ordenadas, y junta cada lista no ordenada con
                su título en la parte superior
    '''
    p1 = re.compile(r'(<li> .+)\n+( *<li>.+)\n+ *', re.UNICODE)
    text1 = p1.sub(r'\1\n\2\n',text)

    p1 = re.compile(r'(<li> .+\n{2,3})(\w)', re.UNICODE)
    text2 = p1.sub(r'\1\n\2',text1)

    p1 = re.compile(r'(.+\.)\n+( *<li>.+)', re.UNICODE)
    text3 = p1.sub(r'\1\n\2',text2)
    return text3





def delete_labels(text):
    '''
        :return:    Texto que se introdujo eliminando las etiquetas <ol> y <h[0-9]>
    '''
    p1 = re.compile(r'<\\*ol>', re.UNICODE)
    text1 = p1.sub(r'',text)

    p2 = re.compile(r'<\\*h[0-9]>', re.UNICODE)
    text2 = p2.sub(r'',text1)
    p3 = re.compile(r'<\\*li>',re.UNICODE)
    text3 = p3.sub(r'',text2)
    return text3




def delete_tabs(text):
    '''
        :return:    Sustituye las tabulaciones por espacios simples
    '''
    p1 = re.compile(r'\t', re.UNICODE)
    text3 = p1.sub(r' ',text)
    return text3




def label_li(text):
    '''
    NO USADA
    :return:    Añade una etiqueta sobre la listas no ordenadas

    '''
    return(re.sub(r'(.+\s+( *<li>.*\s+)+)(.)',r"<full_li>\n\1<\\full_li>\n\3",text,re.UNICODE))




def relabel_ol(text):
    '''
    :return:   Asocia a cada lista ordenada su título correspondiente.
    '''

    p1 = re.compile(r'(.+[\.|\:])\s+<ol>(\n(.+\n)+<\\ol>)', re.UNICODE)
    text2 = p1.sub(r'<ol>\n\1\2',text)
    return text2




# Se encarga de etiquetar las listas de elementos en un texto
def label_lists(text):
    '''
        :return:    Etiqueta las listas con <li> y juntando los terminos
                    entre sí y acercándolo a la parte superior
    '''
    texto_procesado = ( delete_listCHR(text)    | p(delete_CID)
                                                | p(delete_emptyListCHR)
                       )
    return texto_procesado



def process_lists(text):
    '''
        :return:    Se encarga de procesar la gestión de las diferentes listas
                    no ordenadas.
    '''
   
    texto_procesado = ( correct_labeling(text)   | p(delete_list_jumps)
                                                    | p(delete_double_endline_list)
                                                    | p(delete_list_doublejumps)
                                                    | p(delete_double_jump_start)
                       )
    return texto_procesado



