import tkinter as tk


def display(d, l):
    root = tk.Tk()
    root.title("Simplex")
    # define a largura e altura da janela de acordo com as dimensões da tela
    width = root.winfo_screenwidth() // 2
    height = root.winfo_screenheight() // 2
    root.geometry(f"{width}x{height}")

    # cria um objeto Canvas para exibir o resultado
    canvas = tk.Canvas(root)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # cria um objeto Scrollbar para permitir a rolagem do conteúdo do Canvas
    scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # associa o Scrollbar ao Canvas
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # cria um Frame dentro do Canvas para exibir o conteúdo
    content = tk.Frame(canvas)
    canvas.create_window((width//2, height//2), window=content, anchor=tk.S)
    # canvas.create_window((0, 0), window=content, anchor=tk.NW)
    
    iteration_num = 0
    for data in d:
        iteration_num += 1
        iteration_label = tk.Label(
            content, text=f"Interação {iteration_num}", font=("Arial", 12, "bold"), pady=5)
        iteration_label.pack()
        table = tk.Frame(content)
        table.pack()
        header1 = tk.Label(table, text="Variável Básica", font=(
            "Helvetica", 12, "bold"), padx=10, pady=5, borderwidth=1, relief=tk.SOLID)
        header1.grid(row=0, column=0, sticky="nsew")
        max_elements = max([len(value_list) for value_list in data.values()])
        for i in range(max_elements):
            header = tk.Label(table, text=l[i], font=(
                "Arial", 12, "bold"), padx=10, pady=5, borderwidth=1, relief=tk.SOLID)
            header.grid(row=0, column=i+1, sticky="nsew")
        row_num = 1
        for key, value_list in data.items():
            row_label = tk.Label(table, text=key, font=(
                "Arial", 10), padx=10, pady=5, borderwidth=1, relief=tk.SOLID)
            row_label.grid(row=row_num, column=0, sticky="nsew")
            for i, value in enumerate(value_list):
                row_value = tk.Label(table, text=value, font=(
                    "Arial", 10), padx=10, pady=5, borderwidth=1, relief=tk.SOLID)
                row_value.grid(row=row_num, column=i+1, sticky="nsew")
                if row_num % 2 == 0:
                    row_label.configure(bg="#f2f2f2")
                    row_value.configure(bg="#f2f2f2")
            row_num += 1
    last = d[-1]
    k = last.keys()
    l = l[:int(len(l)/2)]
    print(l)
    print('z', ':', last['z'][-1])
    iteration_label = tk.Label(
        content, text='z'+':'+str(last['z'][-1]), font=("Arial", 12, "bold"), pady=5)
    iteration_label.pack()
    for i in l:
        if i in k:
            iteration_label = tk.Label(
                content, text=i+':'+str(last[i][-1]), font=("Arial", 12, "bold"), pady=5)
            iteration_label.pack()
        else:
            iteration_label = tk.Label(
                content, text=i+':'+str(0), font=("Arial", 12, "bold"), pady=5)
            iteration_label.pack()
    root.mainloop()
