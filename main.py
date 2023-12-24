import sys
import sqlite3
from functools import partial

from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QPushButton, QSpinBox, QMessageBox
from ui import *

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.main_ui = Ui_MainWindow()
        self.main_ui.setupUi(self)

        self.setWindowTitle("PCParts")

        self.main_ui.tableProduct.setColumnWidth(0, 90)
        self.main_ui.tableProduct.setColumnWidth(1, 155)
        self.main_ui.tableProduct.setColumnWidth(5, 144)
        self.main_ui.tableProduct.setColumnWidth(6, 85)

        self.main_ui.tableCollectOrder.setColumnWidth(0, 90)
        self.main_ui.tableCollectOrder.setColumnWidth(1, 100)
        self.main_ui.tableCollectOrder.setColumnWidth(2, 89)
        self.main_ui.tableCollectOrder.setColumnWidth(3, 59)

        self.main_ui.pushButton_Product.clicked.connect(self.clickProduct)
        self.main_ui.pushButton_AddProductMove.clicked.connect(self.clickAddProductMove)
        self.main_ui.pushButton_ChangeProductMove.clicked.connect(self.clickChangeProductMove)
        self.main_ui.tableProduct.doubleClicked.connect(self.clickChangeProductMove)
        self.main_ui.pushButton_DeleteProduct.clicked.connect(self.clickDeleteProduct)
        self.main_ui.pushButton_CreateOrder.clicked.connect(self.clickCreateOrder)
        self.main_ui.pushButton_AddProduct.clicked.connect(self.clickAddProduct)
        self.main_ui.pushButton_CancelAddProduct.clicked.connect(self.clickCancelAddChangeProduct)
        self.main_ui.pushButton_ChangeProduct.clicked.connect(self.clickChangeProduct)
        self.main_ui.pushButton_CancelChangeProduct.clicked.connect(self.clickCancelAddChangeProduct)
        self.selected_product_id = None

        self.main_ui.pushButton_Category.clicked.connect(self.clickCategory)
        self.main_ui.pushButton_AddCategoryMove.clicked.connect(self.clickAddCategoryMove)
        self.main_ui.pushButton_ChangeCategoryMove.clicked.connect(self.clickChangeCategoryMove)
        self.main_ui.tableCategory.doubleClicked.connect(self.clickChangeCategoryMove)
        self.main_ui.pushButton_DeleteCategory.clicked.connect(self.clickDeleteCategory)
        self.main_ui.pushButton_AddCategory.clicked.connect(self.clickAddCategory)
        self.main_ui.pushButton_CancelAddCategory.clicked.connect(self.clickCancelAddChangeCategory)
        self.main_ui.pushButton_ChangeCategory.clicked.connect(self.clickChangeCategory)
        self.main_ui.pushButton_CancelChangeCategory.clicked.connect(self.clickCancelAddChangeCategory)

        self.main_ui.pushButton_Order.clicked.connect(self.clickOrder)
        self.main_ui.pushButton_DeleteOrder.clicked.connect(self.clickDeleteOrder)
        self.main_ui.pushButton_OrderInfoMove.clicked.connect(self.clickOrderInfoMove)
        self.main_ui.tableOrder.doubleClicked.connect(self.clickOrderInfoMove)
        self.main_ui.pushButton_CancelOrderInfo.clicked.connect(self.clickCancelOrderInfo)

        self.main_ui.pushButton_Report.clicked.connect(self.clickReport)
        self.main_ui.pushButton_CreateReport.clicked.connect(self.clickCreateReport)
        self.AddReportType()

        self.connection = sqlite3.connect('torg.db')
        self.cursor = self.connection.cursor()

        self.showCategoryTable()
        self.showProductTable()
        self.showOrderTable()

        self.order_data = {}

        int_validator = QIntValidator()
        self.main_ui.lineEdit_AddQuantyProduct.setValidator(int_validator)
        self.main_ui.lineEdit_ChangeQuantyProduct.setValidator(int_validator)

        double_validator = QDoubleValidator()
        self.main_ui.lineEdit_AddPriceProduct.setValidator(double_validator)
        self.main_ui.lineEdit_ChangePriceProduct.setValidator(double_validator)

    def showOrderTable(self):
        self.main_ui.tableOrder.setRowCount(0)

        self.cursor.execute("SELECT id_order, date_order ,price_order  FROM Orders")
        orders_data = self.cursor.fetchall()

        for row, (id_order, date_order, price_order) in enumerate(orders_data):
            self.main_ui.tableOrder.insertRow(row)
            self.main_ui.tableOrder.setItem(row, 0, QTableWidgetItem(str(id_order)))
            self.main_ui.tableOrder.setItem(row, 1, QTableWidgetItem(str(date_order)))
            self.main_ui.tableOrder.setItem(row, 2, QTableWidgetItem(str(price_order)))

    def showCategoryTable(self):
        self.cursor.execute("SELECT id_category, category_name FROM Category")
        result = self.cursor.fetchall()

        self.main_ui.tableCategory.setRowCount(0)

        for row_num, row_data in enumerate(result):
            self.main_ui.tableCategory.insertRow(row_num)
            for col_num, col_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(col_data))
                self.main_ui.tableCategory.setItem(row_num, col_num, item)

                item.setToolTip(str(col_data))

    def showProductTable(self):
        self.cursor.execute(
            "SELECT id_product, product_name, id_category, quanty_in_stock, unit_price, id_manufacturer FROM Product")
        result = self.cursor.fetchall()

        self.main_ui.tableProduct.setRowCount(0)

        for row_num, row_data in enumerate(result):
            self.main_ui.tableProduct.insertRow(row_num)

            category_id = row_data[2]
            category_name = self.get_category_name(category_id)

            manufacturer_id = row_data[5]
            manufacturer_name = self.get_manufacturer_name(manufacturer_id)

            row_data = list(row_data)
            row_data[2] = category_name
            row_data[5] = manufacturer_name

            for col_num, col_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(col_data))
                self.main_ui.tableProduct.setItem(row_num, col_num, item)

                item.setToolTip(str(col_data))

        row_count = self.main_ui.tableProduct.rowCount()

        for row in range(row_count):
            button = QPushButton("+")
            button.clicked.connect(partial(self.pushButton_AddProductToOrder_clicked, row))

            self.main_ui.tableProduct.setCellWidget(row, self.main_ui.tableProduct.columnCount() - 1, button)

    def get_category_name(self, category_id):
        self.cursor.execute("SELECT category_name FROM Category WHERE id_category = ?", (category_id,))
        result = self.cursor.fetchone()
        return result[0] if result else "Unknown Category"

    def get_manufacturer_name(self, manufacturer_id):
        self.cursor.execute("SELECT manufacturer_name FROM Manufacturer WHERE id_manufacturer = ?", (manufacturer_id,))
        result = self.cursor.fetchone()
        return result[0] if result else "Unknown Manufacturer"

    def update_order_price_label(self):
        total_price = 0
        for product_number, item_data in self.order_data.items():
            quantity = item_data['quantity']
            price = item_data.get('price', 0)
            total_price += quantity * price

        self.main_ui.label_OrderPrice.setText(f"Стоимость заказа: {total_price} руб.")

    def pushButton_AddProductToOrder_clicked(self, row):
        product_number = self.main_ui.tableProduct.item(row, 0).text()
        product_name = self.main_ui.tableProduct.item(row, 1).text()
        available_quantity = int(self.main_ui.tableProduct.item(row, 3).text())
        price = float(self.main_ui.tableProduct.item(row, 4).text())

        if product_number in self.order_data:
            item_data = self.order_data[product_number]
            if item_data['quantity'] < available_quantity:
                item_data['quantity'] += 1
                spin_box = item_data['spin_box']
                spin_box.setValue(item_data['quantity'])
        else:
            current_row = self.main_ui.tableCollectOrder.rowCount()
            self.main_ui.tableCollectOrder.insertRow(current_row)

            self.main_ui.tableCollectOrder.setItem(current_row, 0, QTableWidgetItem(product_number))
            self.main_ui.tableCollectOrder.setItem(current_row, 1, QTableWidgetItem(product_name))

            spin_box = QSpinBox()
            spin_box.setProperty("row", current_row)
            spin_box.setMinimum(0)
            spin_box.setMaximum(available_quantity)
            spin_box.setValue(1)
            spin_box.valueChanged.connect(self.spinBoxQuantityProductInOrder_changed)
            self.main_ui.tableCollectOrder.setCellWidget(current_row, 2, spin_box)

            remove_button = QPushButton("✖")
            remove_button.setProperty("row", current_row)
            remove_button.clicked.connect(self.pushButton_RemoveItem_clicked)
            self.main_ui.tableCollectOrder.setCellWidget(current_row, 3, remove_button)

            for col in range(2):
                item = self.main_ui.tableCollectOrder.item(current_row, col)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)

            self.order_data[product_number] = {'row': current_row, 'quantity': 1, 'spin_box': spin_box, 'price': price}

        self.update_order_price_label()

    def spinBoxQuantityProductInOrder_changed(self, value):
        sender = self.sender()
        row = sender.property("row")
        total_quantity_item = self.main_ui.tableCollectOrder.item(row, 2)

        for col in range(2):
            item = self.main_ui.tableCollectOrder.item(row, col)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        if total_quantity_item is not None:
            total_quantity_item.setText(str(value))
        product_number = self.main_ui.tableCollectOrder.item(row, 0).text()

        self.order_data[product_number]['quantity'] = value

        if value == 0:
            del self.order_data[product_number]
            self.main_ui.tableCollectOrder.removeRow(row)

        self.update_order_price_label()

    def pushButton_RemoveItem_clicked(self):
        try:
            selected_row = self.main_ui.tableCollectOrder.currentRow()

            if selected_row == -1:
                return

            product_number_item = self.main_ui.tableCollectOrder.item(selected_row, 0)

            if product_number_item is None:
                return

            product_number = product_number_item.text()

            if product_number not in self.order_data:
                return

            self.main_ui.tableCollectOrder.removeRow(selected_row)
            del self.order_data[product_number]
            self.update_order_price_label()

        except:
            print(f"Ошибка")

    def clickProduct(self):
        self.showProductTable()
        self.main_ui.stackedWidget.setCurrentIndex(0)

    def clickAddProductMove(self):
        self.AddCategoryAndManufscturer()

        self.main_ui.lineEdit_AddProductName.clear()
        self.main_ui.lineEdit_AddQuantyProduct.clear()
        self.main_ui.lineEdit_AddPriceProduct.clear()

        self.main_ui.stackedWidget.setCurrentIndex(1)

    def clickChangeProductMove(self):
        self.ChangeCategoryAndManufscturer()
        selected_row = self.main_ui.tableProduct.currentRow()

        if selected_row == -1:
            selected_row = 0
            self.main_ui.tableProduct.setCurrentCell(selected_row, 0)

        if selected_row >= 0:
            self.main_ui.lineEdit_ChangeProductName.clear()
            self.main_ui.lineEdit_ChangeQuantyProduct.clear()
            self.main_ui.lineEdit_ChangePriceProduct.clear()
            self.main_ui.comboBox_ChangeCategoryProduct.setCurrentIndex(0)
            self.main_ui.comboBox_ChangeManufacturer.setCurrentIndex(0)
            self.selected_product_id = None

            product_id = int(self.main_ui.tableProduct.item(selected_row, 0).text())
            product_name = self.main_ui.tableProduct.item(selected_row, 1).text()
            category_name = self.main_ui.tableProduct.item(selected_row, 2).text()
            quantity = self.main_ui.tableProduct.item(selected_row, 3).text()
            price = self.main_ui.tableProduct.item(selected_row, 4).text()
            manufacturer_name = self.main_ui.tableProduct.item(selected_row, 5).text()

            self.main_ui.lineEdit_ChangeProductName.setText(product_name)
            self.main_ui.lineEdit_ChangeQuantyProduct.setText(quantity)
            self.main_ui.lineEdit_ChangePriceProduct.setText(price)

            index_category = self.main_ui.comboBox_ChangeCategoryProduct.findText(category_name)
            if index_category != -1:
                self.main_ui.comboBox_ChangeCategoryProduct.setCurrentIndex(index_category)

            index_manufacturer = self.main_ui.comboBox_ChangeManufacturer.findText(manufacturer_name)
            if index_manufacturer != -1:
                self.main_ui.comboBox_ChangeManufacturer.setCurrentIndex(index_manufacturer)

            self.selected_product_id = product_id

        self.main_ui.stackedWidget.setCurrentIndex(2)

    def clickDeleteProduct(self):
        selected_row = self.main_ui.tableProduct.currentRow()
        if selected_row >= 0:
            id_to_delete = int(self.main_ui.tableProduct.item(selected_row, 0).text())
            self.cursor.execute("DELETE FROM Product WHERE id_product = ?", (id_to_delete,))
            self.connection.commit()
            self.showProductTable()

    def clickAddProduct(self):
        category = self.main_ui.comboBox_AddCategoryProduct.currentText()
        manufacturer = self.main_ui.comboBox_AddManufacturer.currentText()
        price = self.main_ui.lineEdit_AddPriceProduct.text()
        product_name = self.main_ui.lineEdit_AddProductName.text()
        quantity = self.main_ui.lineEdit_AddQuantyProduct.text()

        if not product_name:
            self.main_ui.label_3.setStyleSheet("color: red;")
            return

        if float(price) < 0:
            price = str(float(price) * -1)

        if int(quantity) < 0:
            quantity = str(int(quantity) * -1)

        self.cursor.execute("SELECT id_category FROM Category WHERE category_name = ?", (category,))
        id_category = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT id_manufacturer FROM Manufacturer WHERE manufacturer_name = ?", (manufacturer,))
        id_manufacturer = self.cursor.fetchone()[0]

        try:
            self.cursor.execute("""
                        INSERT INTO Product (product_name, id_category, unit_price, id_manufacturer, quanty_in_stock)
                        VALUES (?, ?, ?, ?, ?)
                    """, (product_name, id_category, price, id_manufacturer, quantity))
        except:
            self.connection.rollback()
            print(f"Ошибка при добавлении товара")
            return

        self.connection.commit()
        self.main_ui.lineEdit_AddPriceProduct.clear()
        self.main_ui.lineEdit_AddProductName.clear()
        self.main_ui.lineEdit_AddQuantyProduct.clear()
        self.main_ui.label_3.setStyleSheet("color: black;")
        self.showProductTable()
        self.main_ui.stackedWidget.setCurrentIndex(0)

    def AddCategoryAndManufscturer(self):
        self.main_ui.comboBox_AddCategoryProduct.clear()
        self.cursor.execute("SELECT category_name FROM Category")
        result = self.cursor.fetchall()

        for category_name in result:
            self.main_ui.comboBox_AddCategoryProduct.addItem(category_name[0])

        self.main_ui.comboBox_AddManufacturer.clear()
        self.cursor.execute("SELECT manufacturer_name FROM Manufacturer")
        result = self.cursor.fetchall()

        for category_name in result:
            self.main_ui.comboBox_AddManufacturer.addItem(category_name[0])

    def ChangeCategoryAndManufscturer(self):
        self.main_ui.comboBox_ChangeCategoryProduct.clear()
        self.cursor.execute("SELECT category_name FROM Category")
        result = self.cursor.fetchall()
        for category_name in result:
            self.main_ui.comboBox_ChangeCategoryProduct.addItem(category_name[0])
        self.main_ui.comboBox_ChangeManufacturer.clear()
        self.cursor.execute("SELECT manufacturer_name FROM Manufacturer")
        result = self.cursor.fetchall()

        for category_name in result:
            self.main_ui.comboBox_ChangeManufacturer.addItem(category_name[0])

    def clickChangeProduct(self):
        product_name = self.main_ui.lineEdit_ChangeProductName.text()
        quantity = self.main_ui.lineEdit_ChangeQuantyProduct.text()
        price = self.main_ui.lineEdit_ChangePriceProduct.text()
        category_name = self.main_ui.comboBox_ChangeCategoryProduct.currentText()
        manufacturer_name = self.main_ui.comboBox_ChangeManufacturer.currentText()

        if not product_name:
            self.main_ui.label_10.setStyleSheet("color: red;")
            return

        if not price:
            price = "0"

        if not quantity:
            quantity = "0.0"

        if float(price) < 0:
            price = str(float(price) * -1)

        if int(quantity) < 0:
            quantity = str(int(quantity) * -1)

        try:
            self.cursor.execute("SELECT id_category FROM Category WHERE category_name = ?", (category_name,))
            id_category = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT id_manufacturer FROM Manufacturer WHERE manufacturer_name = ?",
                                (manufacturer_name,))
            id_manufacturer = self.cursor.fetchone()[0]

            self.cursor.execute("""
                            UPDATE Product 
                            SET product_name=?, id_category=?, unit_price=?, id_manufacturer=?, quanty_in_stock=?
                            WHERE id_product=?
                        """, (product_name, id_category, price, id_manufacturer, quantity, self.selected_product_id))
            print("ошибка 3")
        except:
            self.connection.rollback()
            print(f"Ошибка при изменении товара")
        self.connection.commit()

        self.main_ui.lineEdit_ChangeProductName.clear()
        self.main_ui.lineEdit_ChangeQuantyProduct.clear()
        self.main_ui.lineEdit_ChangePriceProduct.clear()
        self.main_ui.comboBox_ChangeCategoryProduct.clear()
        self.main_ui.comboBox_ChangeManufacturer.clear()
        self.selected_product_id = None

        self.main_ui.label_10.setStyleSheet("color: black;")

        self.showProductTable()

        self.main_ui.stackedWidget.setCurrentIndex(0)

    def clickCancelAddChangeProduct(self):
        self.main_ui.lineEdit_AddProductName.clear()
        self.main_ui.lineEdit_AddQuantyProduct.clear()
        self.main_ui.lineEdit_AddPriceProduct.clear()
        self.main_ui.stackedWidget.setCurrentIndex(0)

    def clickCreateOrder(self):
        client_full_name = self.main_ui.lineEdit_ClientFullName.text().strip()
        client_contact = self.main_ui.lineEdit_ClientNumber.text().strip()

        if client_full_name and ' ' in client_full_name:
            if not self.order_data:
                QMessageBox.warning(self, " ", "Добавьте товары в заказ перед созданием.")
                return

            client_surname, client_name = client_full_name.split(' ', 1)

            current_date_time = QDateTime.currentDateTime().toString("yyyy-MM-dd")

            total_price = 0
            for product_number, item_data in self.order_data.items():
                quantity = item_data['quantity']
                price = item_data.get('price', 0)
                total_price += quantity * price

            try:
                self.connection.commit()

                self.cursor.execute(
                    "INSERT INTO Orders (client_surname, client_name, client_contact, date_order, price_order) VALUES (?, ?, ?, ?, ?)",
                    (client_surname, client_name, client_contact, current_date_time, total_price)
                )
                new_order_id = self.cursor.lastrowid

                for product_number, item_data in self.order_data.items():
                    id_product = int(product_number)
                    quantity_in_order = item_data['quantity']

                    self.cursor.execute(
                        "INSERT INTO OrderProduct (id_order, id_product, quanty_product_in_order) VALUES (?, ?, ?)",
                        (new_order_id, id_product, quantity_in_order)
                    )

                    current_quantity = self.get_current_quantity_in_stock(id_product)
                    new_quantity = current_quantity - quantity_in_order

                    self.cursor.execute(
                        "UPDATE Product SET quanty_in_stock = ? WHERE id_product = ?",
                        (new_quantity, id_product)
                    )

                self.connection.commit()

                self.main_ui.lineEdit_ClientFullName.clear()
                self.main_ui.lineEdit_ClientNumber.clear()
                self.order_data = {}
                self.main_ui.tableCollectOrder.setRowCount(0)
                self.update_order_price_label()

                self.showProductTable()

                QMessageBox.information(self, " ", f"Заказ успешно создан!")
                self.main_ui.labelClientFullName.setStyleSheet("color: black;")

            except:
                self.connection.rollback()
                QMessageBox.warning(self, " ", f"Произошла ошибка при создании заказа")

        else:
            self.main_ui.labelClientFullName.setStyleSheet("color: red")

    def get_current_quantity_in_stock(self, id_product):

        self.cursor.execute("SELECT quanty_in_stock FROM Product WHERE id_product = ?", (id_product,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return 0

    def clickCategory(self):
        self.showCategoryTable()
        self.main_ui.stackedWidget.setCurrentIndex(3)

    def clickAddCategoryMove(self):
        self.main_ui.lineEdit_AddCategory.clear()
        self.main_ui.stackedWidget.setCurrentIndex(4)

    def clickChangeCategoryMove(self):
        selected_row = self.main_ui.tableCategory.currentRow()

        if selected_row == -1:
            selected_row = 0
            self.main_ui.tableCategory.setCurrentCell(selected_row, 0)

        category_id = int(self.main_ui.tableCategory.item(selected_row, 0).text())
        category_name = self.main_ui.tableCategory.item(selected_row, 1).text()

        self.main_ui.lineEdit_ChangeCategory.setText(category_name)

        self.selected_category_id = category_id
        self.selected_category_name = category_name

        self.main_ui.stackedWidget.setCurrentIndex(5)

    def clickDeleteCategory(self):
        selected_row = self.main_ui.tableCategory.currentRow()
        if selected_row >= 0:
            id_to_delete = int(self.main_ui.tableCategory.item(selected_row, 0).text())

            self.cursor.execute("DELETE FROM Category WHERE id_category = ?", (id_to_delete,))
            self.connection.commit()
            self.showCategoryTable()

    def clickAddCategory(self):
        category_name = self.main_ui.lineEdit_AddCategory.text()

        if not category_name:
            self.main_ui.label_AddCategoryName.setStyleSheet("color: red;")
            return
        print(category_name)
        try:
            # Добавление категории в таблицу Category
            self.cursor.execute("""
                                INSERT INTO Category (category_name)
                                VALUES (?)
                            """, (category_name,))
        except:
            self.connection.rollback()

        self.connection.commit()
        self.main_ui.lineEdit_AddCategory.clear()
        self.showCategoryTable()
        self.main_ui.label_AddCategoryName.setStyleSheet("color: black;")
        self.main_ui.stackedWidget.setCurrentIndex(3)

    def clickChangeCategory(self):
        if self.selected_category_id is not None:
            new_category_name = self.main_ui.lineEdit_ChangeCategory.text()

            if not new_category_name:
                self.main_ui.label_ChangeCategoryName.setStyleSheet("color: red;")
                return

            try:
                self.cursor.execute("UPDATE Category SET category_name = ? WHERE id_category = ?",
                                    (new_category_name, self.selected_category_id))
            except:
                self.connection.rollback()

            self.connection.commit()
            self.selected_category_id = None
            self.selected_category_name = None
            self.main_ui.lineEdit_ChangeCategory.clear()
            self.main_ui.label_ChangeCategoryName.setStyleSheet("color: black;")
            self.showCategoryTable()
            self.main_ui.stackedWidget.setCurrentIndex(3)

    def clickCancelAddChangeCategory(self):
        self.main_ui.lineEdit_AddCategory.clear()

        self.main_ui.stackedWidget.setCurrentIndex(3)

    def clickOrder(self):
        self.showOrderTable()
        self.main_ui.stackedWidget.setCurrentIndex(6)

    def clickOrderInfoMove(self):
        selected_items = self.main_ui.tableOrder.selectedItems()

        if not selected_items:
            self.main_ui.tableOrder.selectRow(0)
            selected_items = self.main_ui.tableOrder.selectedItems()

        if not selected_items:
            return

        selected_row = selected_items[0].row()
        id_order = int(self.main_ui.tableOrder.item(selected_row, 0).text())

        self.cursor.execute(
            "SELECT Product.id_product, Product.product_name, OrderProduct.quanty_product_in_order "
            "FROM OrderProduct "
            "JOIN Product ON OrderProduct.id_product = Product.id_product "
            "WHERE OrderProduct.id_order = ?",
            (id_order,))
        order_product_data = self.cursor.fetchall()

        self.main_ui.tableOrderProductInfo.setRowCount(0)

        for row, data in enumerate(order_product_data):
            id_product, product_name, quanty_product_in_order = data

            self.main_ui.tableOrderProductInfo.insertRow(row)

            self.main_ui.tableOrderProductInfo.setItem(row, 0, QtWidgets.QTableWidgetItem(str(id_product)))
            self.main_ui.tableOrderProductInfo.setItem(row, 1, QtWidgets.QTableWidgetItem(product_name))
            self.main_ui.tableOrderProductInfo.setItem(row, 2, QtWidgets.QTableWidgetItem(str(quanty_product_in_order)))

        self.cursor.execute(
            "SELECT id_order, price_order, client_surname, client_name, client_contact FROM Orders WHERE id_order = ?",
            (id_order,))
        order_data = self.cursor.fetchone()

        if order_data:
            id_order, order_price, client_surname, client_name, client_contact = order_data

            self.main_ui.stackedWidget.setCurrentIndex(7)
            self.main_ui.OrderNumber.setText(f"Заказ №{id_order}")
            self.main_ui.label_OrderCost.setText(f"Стоимость заказа: {order_price} руб.")
            self.main_ui.label_ClientSurnameOrder.setText(f"{client_surname}")
            self.main_ui.label_ClientNameOrder.setText(f"{client_name}")
            self.main_ui.label_ClientContactOrder.setText(f"{client_contact}")
        else:
            return

        self.main_ui.stackedWidget.setCurrentIndex(7)

    def clickCancelOrderInfo(self):
        self.main_ui.stackedWidget.setCurrentIndex(6)

    def clickDeleteOrder(self):
        selected_items = self.main_ui.tableOrder.selectedItems()

        if not selected_items:
            return

        selected_row = selected_items[0].row()
        id_order = int(self.main_ui.tableOrder.item(selected_row, 0).text())

        self.cursor.execute("DELETE FROM Orders WHERE id_order = ?", (id_order,))
        self.cursor.execute("DELETE FROM OrderProduct WHERE id_order = ?", (id_order,))
        self.connection.commit()

        self.showOrderTable()

    def clickReport(self):
        self.main_ui.stackedWidget.setCurrentIndex(8)

    def AddReportType(self):
        self.main_ui.comboBox_TypeReport.addItem("Отчет о финансовой активности по месяцам")
        self.main_ui.comboBox_TypeReport.addItem("Отчет суммарной выручки по категориям")

    def clickCreateReport(self):
        report_type = self.main_ui.comboBox_TypeReport.currentText()

        self.main_ui.tableWidget_Report.setRowCount(0)
        self.main_ui.tableWidget_Report.setColumnCount(0)

        if report_type == "Отчет о финансовой активности по месяцам":
            query = """
                SELECT
                    strftime('%m-%Y', Orders.date_order) AS month,
                    COUNT(Orders.id_order) AS total_orders,
                    SUM(Orders.price_order) AS total_revenue,
                    AVG(Orders.price_order) AS average_order_price
                FROM
                    Orders
                WHERE
                    Orders.date_order BETWEEN '2023-01-01' AND '2023-12-31'
                GROUP BY
                    month;
            """
            columns = ["Дата", "Всего заказов", "Общий доход", "Средняя цена заказа"]
        elif report_type == "Отчет суммарной выручки по категориям":
            query = """
                SELECT
                    Category.category_name AS product_category,
                    SUM(Orders.price_order) AS total_revenue
                FROM
                    Product
                JOIN
                    Category ON Product.id_category = Category.id_category
                JOIN
                    OrderProduct ON Product.id_product = OrderProduct.id_product
                JOIN
                    Orders ON OrderProduct.id_order = Orders.id_order
                GROUP BY
                    product_category;
            """
            columns = ["Категория товаров", "Доход"]
        else:
            return

        try:
            self.main_ui.tableWidget_Report.clear()
            self.main_ui.tableWidget_Report.setColumnCount(len(columns))
            self.main_ui.tableWidget_Report.setHorizontalHeaderLabels(columns)

            self.cursor.execute(query)
            report_data = self.cursor.fetchall()

            for row, data in enumerate(report_data):
                self.main_ui.tableWidget_Report.insertRow(row)
                for col, value in enumerate(data):
                    item = QTableWidgetItem(str(value))
                    self.main_ui.tableWidget_Report.setItem(row, col, item)

            table_width = self.main_ui.tableWidget_Report.width()
            total_width = sum(self.main_ui.tableWidget_Report.columnWidth(col) for col in
                              range(self.main_ui.tableWidget_Report.columnCount()))
            scaling_factor = (table_width - 23) / total_width

            for col in range(self.main_ui.tableWidget_Report.columnCount()):
                new_width = self.main_ui.tableWidget_Report.columnWidth(col) * scaling_factor
                self.main_ui.tableWidget_Report.setColumnWidth(col, int(new_width))

        except:
            return

    def __del__(self):
        self.connection.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())