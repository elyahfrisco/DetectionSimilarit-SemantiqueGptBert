import tkinter as tk
from tkinter import filedialog
from sentence_transformers import SentenceTransformer, util
from openai import OpenAI
import threading
import fitz  # PyMuPDF
from docx import Document
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def read_pdf(file_path):
    with fitz.open(file_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text

def read_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def upload_file(text_widget):
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("Word files", "*.docx")])
    if file_path:
        if file_path.endswith('.pdf'):
            text = read_pdf(file_path)
        elif file_path.endswith('.docx'):
            text = read_docx(file_path)
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, text)


global similarity_score
similarity_score = 0 

def detect_plagiarism():
    phrase1 = text1.get("1.0", "end-1c")
    phrase2 = text2.get("1.0", "end-1c")

    embedding1 = model.encode(phrase1, convert_to_tensor=True)
    embedding2 = model.encode(phrase2, convert_to_tensor=True)
    similarite = util.pytorch_cos_sim(embedding1, embedding2)
    similarity_result.set(f"Similarité sémantique : {similarite.item()}")

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Les phrases suivantes sont-elles sémantiquement similaires? Phrase 1: '{phrase1}' Phrase 2: '{phrase2}'",
            }
        ],
        model="gpt-4",
    )
    response_content = chat_completion.choices[0].message.content
    observation_result.set(f"Observation : {response_content}")
    print(f"Valeur de similarité calculée: {similarite.item()}")
    global similarity_score
    similarity_score = max(0, min(similarite.item(), 1))  # Mettre à jour la variable globale
   
    window.after(0, update_chart)
    window.after(0, hide_loading_label)
   

def hide_loading_label():
    loading_label.pack_forget()


def on_detect():
    loading_label.pack()
    threading.Thread(target=detect_plagiarism).start()

def clear_all():
    
    """Fonction pour réinitialiser les champs de texte et les résultats."""
    global canvas_widget
    text1.delete("1.0", tk.END)
    text2.delete("1.0", tk.END)
    similarity_result.set("")
    observation_result.set("")
    if canvas_widget is not None:
        canvas_widget.destroy()
        canvas_widget = None

canvas_widget = None
canvas_widget = None
    
canvas_widget = None  # Déclaration globale au début du script

def update_chart():
    global similarity_score, canvas_widget  # Utilisation de la variable globale
    similarity_percentage = similarity_score * 100  # Convertir en pourcentage

    plt.clf()  # Efface le graphique précédent
    labels = 'Similarité', 'Différence'
    sizes = [similarity_percentage, 100 - similarity_percentage]
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Afficher le graphique dans Tkinter
    canvas = FigureCanvasTkAgg(fig, master=window)  # A Tk.DrawingArea.
    if canvas_widget is not None:
        canvas_widget.destroy()  # Détruire l'ancien widget s'il existe
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()
    canvas.draw()

    


window = tk.Tk()
window.title("Détection de Plagiat")

tk.Label(window, text="Entrer le texte 1 ou uploader un fichier :").pack()
text1 = tk.Text(window, height=8, width=80)
text1.pack()
upload_button1 = tk.Button(window, text="Uploader un fichier", command=lambda: upload_file(text1))
upload_button1.pack(pady=10)

tk.Label(window, text="Entrer le texte 2 ou uploader un fichier :").pack()
text2 = tk.Text(window, height=8, width=80)
text2.pack()
upload_button2 = tk.Button(window, text="Uploader un fichier", command=lambda: upload_file(text2))
upload_button2.pack(pady=10)

detect_button = tk.Button(window, text="Détecter", command=on_detect , bg='green', fg='white')
detect_button.pack(pady=10)

clear_button = tk.Button(window, text="Réinitialiser", command=clear_all, bg='blue', fg='white')
clear_button.pack(pady=10)


similarity_result = tk.StringVar()
tk.Label(window, textvariable=similarity_result).pack()

observation_result = tk.StringVar()
tk.Label(window, textvariable=observation_result).pack()

loading_label = tk.Label(window, text="Chargement...")
loading_label.pack()
loading_label.pack_forget()

model = SentenceTransformer('all-MiniLM-L6-v2')
# enter l'Api Key de Gpt
client = OpenAI(api_key="")


window.mainloop()
