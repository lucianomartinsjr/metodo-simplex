from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QSizePolicy
import sympy
import numpy as np
import simply
M = sympy.Symbol('M', positive=True)
HEADER_SPACE = 11


class MainWindow(QMainWindow):
    def __init__(simplex):
        super(MainWindow, simplex).__init__()
        simplex.setWindowTitle("Algoritimo Simplex")
        # Você pode escolher entre <=, >=, ou = para restrição.
        simplex.CONSTRAINT_EQUALITY_SIGNS = [u"\u2264", u"\u2265", "="]
        # Lista para acompanhar todos os novos widgets criados (como aqueles para mostrar iteração) para que possam ser facilmente excluídos.
        simplex.new_widgets = []
        simplex.create_ui()
        simplex.set_ui_layout()

        simplex.setFixedWidth(simplex.sizeHint().width()+100)
        simplex.setWindowFlags(Qt.WindowCloseButtonHint |
                               Qt.WindowMinimizeButtonHint)

    def create_ui(simplex):
        simplex.objective_function_label = QLabel("Função Objetivo", simplex)
        simplex.objective_function_label.setFixedHeight(
            simplex.objective_function_label.sizeHint().height())
        simplex.objective_fxn_table = simplex.create_table(
            1, 4, ["="], simplex.create_header_labels(2))

        z_item = QTableWidgetItem("Z")
        simplex.objective_fxn_table.setItem(0, 3, z_item)
        z_item.setFlags(Qt.ItemIsEnabled)

        # ajustar o tamanho da tabela de função objetivo para que ela se ajuste perfeitamente às linhas
        simplex.objective_fxn_table.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Minimum)
        simplex.objective_fxn_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        simplex.objective_fxn_table.resizeColumnsToContents()
        simplex.objective_fxn_table.setFixedHeight(simplex.objective_fxn_table.verticalHeader(
        ).length()+simplex.objective_fxn_table.horizontalHeader().height())

        simplex.constraints_label = QLabel("Matriz das restrições", simplex)
        simplex.constraints_label.setFixedHeight(
            simplex.constraints_label.sizeHint().height())
        simplex.constraint_table = simplex.create_table(
            2, 4, simplex.CONSTRAINT_EQUALITY_SIGNS, simplex.create_header_labels(2))
        simplex.constraint_table.setFixedHeight(
            simplex.constraint_table.sizeHint().height())

        simplex.answers_label = QLabel()

        simplex.add_col_btn = QPushButton('( + ) Adicionar variável', simplex)
        simplex.add_col_btn.clicked.connect(simplex.add_column_event)
        simplex.del_col_btn = QPushButton("( - ) Apagar variável", simplex)
        simplex.del_col_btn.clicked.connect(simplex.del_col_event)
        simplex.add_row_btn = QPushButton('( + ) Adicionar restrição', simplex)
        simplex.add_row_btn.clicked.connect(simplex.add_row_event)
        simplex.del_row_btn = QPushButton("( - ) Apagar restrição", simplex)
        simplex.del_row_btn.clicked.connect(simplex.del_row_event)

        simplex.solve_btn = QPushButton('Resolver', simplex)
        simplex.solve_btn.clicked.connect(simplex.resolver)

        simplex.operation_combo = QComboBox()
        for item in ["Maximizar", "Minimizar"]:
            simplex.operation_combo.addItem(item)

    def set_ui_layout(simplex):
        vbox_layout1 = QHBoxLayout(simplex)
        simplex.vbox_layout2 = QVBoxLayout(simplex)

        vbox_layout1.addWidget(simplex.add_col_btn)
        vbox_layout1.addWidget(simplex.del_col_btn)
        vbox_layout1.addWidget(simplex.add_row_btn)
        vbox_layout1.addWidget(simplex.del_row_btn)
        vbox_layout1.addWidget(simplex.operation_combo)
        vbox_layout1.addWidget(simplex.solve_btn)

        central_widget = QWidget(simplex)
        simplex.setCentralWidget(central_widget)

        main_v_layout = QVBoxLayout(simplex)
        central_widget.setLayout(main_v_layout)

        simplex.vbox_layout2.addWidget(simplex.objective_function_label)
        simplex.vbox_layout2.addWidget(simplex.objective_fxn_table)
        simplex.vbox_layout2.addWidget(simplex.constraints_label)
        simplex.vbox_layout2.addWidget(simplex.constraint_table)
        simplex.vbox_layout2.addWidget(simplex.answers_label)

        main_v_layout.addLayout(vbox_layout1)
        main_v_layout.addLayout(simplex.vbox_layout2)

    def create_table(simplex, rows, cols, equality_signs=None, horizontal_headers=None, vertical_headers=None):
        table = QTableWidget(simplex)
        table.setColumnCount(cols)
        table.setRowCount(rows)

        # Set the table headers
        if horizontal_headers:
            table.setHorizontalHeaderLabels(horizontal_headers)

        if vertical_headers:
            table.setVerticalHeaderLabels(vertical_headers)

        # Adicione os sinais de <=, >= ou = para que a pessoa possa selecionar se a restrição é <=, >= ou =
        # sso também é usado para a função objetivo, mas na função objetivo, usamos apenas = Z, então um sinal [=] é passado
        # para os sinais de igualdade na criação da tabela de função objetivo na função create_ui.
        if equality_signs:
            numofrows = table.rowCount()
            numofcols = table.columnCount()
            # adicionar combo itens para a tabela simplex.constraint_table
            for index in range(numofrows):
                equality_signs_combo = QComboBox()
                for item in equality_signs:
                    equality_signs_combo.addItem(item)
                table.setCellWidget(index, numofcols - 2, equality_signs_combo)

        # Do the resize of the columns by content Faz o reajuste das colunas
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        return table

    def create_header_labels(simplex, num_of_variables):
        """Nome das colunas para as tabelas x1,x2,...."""
        header_labels = [" "*HEADER_SPACE + "x" +
                         str(i + 1) + " " * HEADER_SPACE for i in range(num_of_variables)]
        header_labels.extend(
            [" " * HEADER_SPACE, " " * HEADER_SPACE + "Igual" + " " * HEADER_SPACE])
        return header_labels

    def del_row_event(simplex):
        # Permitir um máximo de uma restrição.
        if simplex.constraint_table.rowCount() > 1:
            simplex.constraint_table.removeRow(
                simplex.constraint_table.rowCount()-1)

    def del_col_event(simplex):
        # Se tivermos x1,x2 e as colunas de sinais e igual não permitirem exclusão de colunas, então não exclua. Caso contrário, exclua.
        if simplex.constraint_table.columnCount() > 4:
            simplex.constraint_table.removeColumn(
                simplex.constraint_table.columnCount()-3)
            simplex.objective_fxn_table.removeColumn(
                simplex.objective_fxn_table.columnCount()-3)

    def add_column_event(simplex):
        simplex.constraint_table.insertColumn(
            simplex.constraint_table.columnCount()-2)
        simplex.objective_fxn_table.insertColumn(
            simplex.objective_fxn_table.columnCount()-2)
        simplex.constraint_table.setHorizontalHeaderLabels(
            simplex.create_header_labels(simplex.constraint_table.columnCount()-2))
        simplex.objective_fxn_table.setHorizontalHeaderLabels(
            simplex.create_header_labels(simplex.constraint_table.columnCount()-2))

        # make the objective fxn table's size fit perfectly with the rows and columns
        simplex.objective_fxn_table.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Minimum)
        simplex.objective_fxn_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        simplex.objective_fxn_table.setFixedHeight(simplex.objective_fxn_table.verticalHeader(
        ).length() + simplex.objective_fxn_table.horizontalHeader().height())

    def add_row_event(simplex):
        simplex.constraint_table.insertRow(simplex.constraint_table.rowCount())
        equality_signs_combo = QComboBox()
        for item in simplex.CONSTRAINT_EQUALITY_SIGNS:
            equality_signs_combo.addItem(item)
        simplex.constraint_table.setCellWidget(simplex.constraint_table.rowCount(
        )-1, simplex.constraint_table.columnCount() - 2, equality_signs_combo)
        simplex.constraint_table.resizeRowsToContents()

    def resolver(simplex):
        tablee = simplex.form_unaugmented_matrix()

        tab = np.flip(tablee)
        tab = tab.tolist()
        # print(tab)

        rowc = len(tab)

        l = []
        soln = []

        for i in tab:
            soln.append(i[-1])
            l.append(i[:-1])
        # print("List",l)

        artifical = np.identity(rowc-1)
        artifical = artifical.tolist()
        artifical = artifical[::-1]
        print(artifical)

        weird = []
        zeros = np.zeros(rowc-1).tolist()
        for i in range(rowc):
            if (i == rowc-1):
                temp = l[i][::-1] + zeros + [0]
            else:
                temp = l[i][::-1] + artifical[i] + [soln[i]]
            weird.append(temp)
        weird = weird[::-1]
        # zvalue make  -ve
        for i in range(len(weird[0])):
            weird[0][i] = -1*weird[0][i]
        opr = simplex.operation_combo.currentText()
        dic1 = {}

        xivalues = ['x1', 'x2', 'x3', 'x4', 'x5', 'x6']
        sivalues = ['s1', 's2', 's3', 's4', 's5', 's6']
        zopt = 'z'

        intialtab = [zopt]+sivalues[:rowc-1]
        for i in range(len(intialtab)):
            dic1[intialtab[i]] = weird[i]
        print("dic1", dic1)

        l4 = xivalues[:rowc] + sivalues[:rowc]
        l1 = weird
        if (opr == 'Minimizar'):
            print("hi")

            def minimizar(l, dic, l4):
                minimum = max(l[0][:-1])
                z = l[0].index(minimum)
                length = len(l[0])
                ratio = []
                for i in l:
                    if (i[z] != 0 and i[z] > 0):
                        ratio.append(i[length-1]/i[z])
                    else:
                        ratio.append(10000)
                # print(ratio[1:])
                z1 = min(ratio[1:])
                # print(z1)
                pivot_column_index = z
                pivot_row_index = ratio.index(z1)
                pivot_row = l[pivot_row_index]
                # print(pivot_row)
                pivot = l[pivot_row_index][pivot_column_index]
                new_pivot_row = []
                for i in pivot_row:
                    new_pivot_row.append(i/pivot)
                # print(new_pivot_row)
                new_table = []
                # print(l)
                for i in range(len(l)):
                    temp = []
                    for j in range(len(l[0])):
                        if (i != pivot_row_index):
                            temp.append(
                                l[i][j]-l[i][pivot_column_index]*new_pivot_row[j])
                        else:
                            temp.append(new_pivot_row[j])
                    new_table.append(temp)
                d = {}
                d1 = list(dic)
                for i in range(len(new_table)):
                    if i == pivot_row_index:
                        d[l4[z]] = new_table[i]
                    else:
                        d[d1[i]] = new_table[i]
                print(d)
                return d
            m = max(l1[0])
            print("Primeira iteraçào :")
            print(l1)
            print(m)
            c = 1
            d = [dic1]
            while ((m > 0) and (m != 0)):
                print("Iteração ", c, ":")
                d2 = minimizar(l1, dic1, l4)
                d.append(d2)
                l2 = list(d2.values())
                for i in l2:
                    print(i)
                m = max(l2[0])
                dic1 = d2
                l1 = l2
                c = c+1
            l5 = l4
            l5.append('Solução')
            simply.display(d, l5)
        else:
            def maximizar(l, dic, l4):
                minimo = min(l[0][:-1])
                z = l[0].index(minimo)
                tamanho = len(l[0])
                razao = []
                for i in l:
                    if (i[z] != 0 and i[z] > 0):
                        razao.append(i[tamanho-1]/i[z])
                    else:
                        razao.append(10000)
                # print(ratio)
                z1 = min(razao[1:])
                # print(z1)
                indice_coluna_pivo = z
                indice_linha_pivo = razao.index(z1)
                linha_pivo = l[indice_linha_pivo]
                # print(pivot_row)
                pivo = l[indice_linha_pivo][indice_coluna_pivo]
                nova_linha_pivo = []
                for i in linha_pivo:
                    nova_linha_pivo.append(i/pivo)
                # print(new_pivot_row)
                nova_tabela = []
                # print(l)
                for i in range(len(l)):
                    temp = []
                    for j in range(len(l[0])):
                        if (i != indice_linha_pivo):
                            temp.append(
                                l[i][j]-l[i][indice_coluna_pivo]*nova_linha_pivo[j])
                        else:
                            temp.append(nova_linha_pivo[j])
                    nova_tabela.append(temp)
                d = {}
                d1 = list(dic)
                for i in range(len(nova_tabela)):
                    if i == indice_linha_pivo:
                        d[l4[z]] = nova_tabela[i]
                    else:
                        d[d1[i]] = nova_tabela[i]
                print(d)
                return d

            m = min(l1[0])
            print("Interação 1 :")
            print(l1)
            print(m)
            c = 1
            d = [dic1]
            while ((m < 0) and (m != 0)):
                print("Interação ", c, ":")
                d2 = maximizar(l1, dic1, l4)
                d.append(d2)
                l2 = list(d2.values())
                for i in l2:
                    print(i)
                m = min(l2[0])
                dic1 = d2
                l1 = l2
                c = c+1
            l5 = l4
            l5.append('Solução')
            simply.display(d, l5)

        """waring
                w = QWidget()
                QMessageBox.warning(w, "Problema é ilimitado. Verifique a formulação do problema. Mostrando apenas as iterações.")
                simplex.answers_label.setText(" ")
                break"""

    def form_unaugmented_matrix(simplex):
        obj_fxn = simplex.obter_obj_fxn()
        table = simplex.constraint_table
        split1_of_constraints = simplex.ler_itens_tabela(simplex.constraint_table, 0, simplex.constraint_table.rowCount(), 0,
                                                         simplex.constraint_table.columnCount() - 2)
        split2_of_constraints = simplex.ler_itens_tabela(simplex.constraint_table, 0, simplex.constraint_table.rowCount(),
                                                         simplex.constraint_table.columnCount() - 1,
                                                         simplex.constraint_table.columnCount())
        unaugmented_matrix_without_obj_fxn = np.concatenate((np.array(split2_of_constraints), split1_of_constraints),
                                                            axis=1)
        unaugmented_matrix = np.vstack(
            (obj_fxn, unaugmented_matrix_without_obj_fxn))
        return unaugmented_matrix

    def ler_itens_tabela(simplex, table, start_row, end_row, start_col, end_col):
        read_table = np.zeros(
            (end_row-start_row, end_col-start_col), dtype=sympy.Symbol)
        for i in range(start_row, end_row):
            for j in range(start_col, end_col):
                read_table[i-end_row][j -
                                      end_col] = float(table.item(i, j).text())

        return read_table

    def ler_sinais_igualdade(simplex, equality_signs_column, table):
        equality_signs = []
        for i in range(table.rowCount()):
            equality_signs.append(table.cellWidget(
                i, equality_signs_column).currentText())
        return equality_signs

    def popularTabela(simplex, table, mylist, start_row, end_row, start_col, end_col):
        for i in range(start_row, end_row):
            for j in range(start_col, end_col):
                table.setItem(i, j, QTableWidgetItem(
                    str(mylist[i - end_row][j - end_col])))
        table.resizeColumnsToContents()

    def obter_obj_fxn(simplex):
        obj_fxn_coeff = simplex.ler_itens_tabela(simplex.objective_fxn_table, 0, simplex.objective_fxn_table.rowCount(
        ), 0, simplex.objective_fxn_table.columnCount()-2)
        obj_fxn = np.insert(obj_fxn_coeff, 0, 0)
        return obj_fxn

    def criar_interface_tabela(simplex, tableau, all_variables, vertical_headers):
        rows, cols = tableau.shape
        gui_tableau = simplex.create_table(
            rows, cols, equality_signs=None, horizontal_headers=all_variables, vertical_headers=vertical_headers)
        simplex.popularTabela(gui_tableau, tableau, 0, rows, 0, cols)
        return gui_tableau

    def update_gui_tableau(simplex, tableau, gui_tableau, current_row, vertical_headers):
        # criar novas linhas
        rows, cols = tableau.shape
        for i in range(rows):
            gui_tableau.insertRow(gui_tableau.rowCount())
        simplex.popularTabela(gui_tableau, tableau, current_row,
                              current_row+rows, 0, cols)
        gui_tableau.setVerticalHeaderLabels(vertical_headers)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
