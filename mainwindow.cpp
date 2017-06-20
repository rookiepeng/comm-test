/*
//    mainwindow.cpp
//
//    Copyright (C) 2017  Zach (Zhengyu) Peng, https://zpeng.me
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    You should have received a copy of the GNU General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "mainwindow.h"
#include "ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    initUI();
    findLocalIPs();
    loadSettings();
    setupConnection();
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::initUI()
{
    QString rule = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])";
    ui->lineEdit_targetIP->setValidator(new QRegExpValidator(QRegExp("^" + rule + "\\." + rule + "\\." + rule + "\\." + rule + "$"), this));
    ui->lineEdit_targetPort->setValidator(new QIntValidator(0, 65535, this));
    ui->lineEdit_listenPort->setValidator(new QIntValidator(0, 65535, this));

    ui->textBrowser_message->setFocusPolicy(Qt::NoFocus);

    ui->lineEdit_send->setFocusPolicy(Qt::StrongFocus);
    ui->lineEdit_send->setFocus();

    ui->comboBox_TCPUDP->addItems(TCPUDPComboList);

    ui->comboBox_serverClient->addItems(ServerClientComboList);

    tableFormat.setBorder(0);

    connect(ui->lineEdit_targetIP, SIGNAL(textChanged(QString)), this, SLOT(enableUpdateButton()));
    connect(ui->lineEdit_targetPort, SIGNAL(textChanged(QString)), this, SLOT(enableUpdateButton()));
    connect(ui->lineEdit_listenPort, SIGNAL(textChanged(QString)), this, SLOT(enableUpdateButton()));
    connect(ui->comboBox_TCPUDP, SIGNAL(currentIndexChanged(int)), this, SLOT(enableUpdateButton()));
    connect(ui->comboBox_serverClient, SIGNAL(currentIndexChanged(int)), this, SLOT(enableUpdateButton()));
    connect(ui->comboBox_TCPUDP, SIGNAL(currentIndexChanged(int)), this, SLOT(disableComboBox(int)));
}

void MainWindow::setupConnection()
{
    targetAddr.setAddress(ui->lineEdit_targetIP->text());
    targetPort = ui->lineEdit_targetPort->text().toInt();
    localAddr.setAddress(ui->comboBox_localIP->currentText());

    connect(ui->pushButton_send, SIGNAL(clicked()), this, SLOT(sendMessage()));
    connect(ui->lineEdit_send, SIGNAL(returnPressed()), this, SLOT(sendMessage()));
    connect(ui->updateButton, SIGNAL(clicked()), this, SLOT(updateConfig()));

    if (getProtocolValue() == TCP)
    {
        if(getRoleValue()==SERVER)
        {
            mytcpserver = new MyTCPServer;
            mytcpserver->listen(localAddr, ui->lineEdit_listenPort->text().toInt());
        }
        else if(getRoleValue()==CLIENT)
        {
            mytcpclient=new MyTCPClient;
            mytcpclient->connectTo(targetAddr,targetPort);
        }
    }
    else if (getProtocolValue() == UDP)
    {
        myudp = new MyUDP;
        connect(myudp, SIGNAL(newMessage(QString, QString)), this, SLOT(appendMessage(QString, QString)));
        connect(myudp, SIGNAL(bindSuccess(bool)), this, SLOT(udpBinded(bool)));
        myudp->bindPort(localAddr, ui->lineEdit_listenPort->text().toInt());
    }
}

void MainWindow::appendMessage(const QString &from, const QString &message)
{
    if (from.isEmpty() || message.isEmpty())
        return;

    QTextCursor cursor(ui->textBrowser_message->textCursor());
    cursor.movePosition(QTextCursor::End);

    QTextTable *table = cursor.insertTable(1, 2, tableFormat);
    table->cellAt(0, 0).firstCursorPosition().insertText('<' + from + "> ");
    table->cellAt(0, 1).firstCursorPosition().insertText(message);
    QScrollBar *bar = ui->textBrowser_message->verticalScrollBar();
    bar->setValue(bar->maximum());
}

void MainWindow::sendMessage()
{
    QString text = ui->lineEdit_send->text();
    if (text.isEmpty())
        return;

    //    if (text.startsWith(QChar('/')))
    //    {
    //        QColor color = ui->textBrowser_message->textColor();
    //        ui->textBrowser_message->setTextColor(Qt::red);
    //        ui->textBrowser_message->append(tr("! Unknown command: %1")
    //                                        .arg(text.left(text.indexOf(' '))));
    //        ui->textBrowser_message->setTextColor(color);
    //    }
    //    else
    //    {
    myudp->sendMessage(targetAddr, targetPort, text);
    appendMessage("client", text);
    //}

    ui->lineEdit_send->clear();
}

void MainWindow::udpBinded(bool isBinded)
{
    ui->updateButton->setDisabled(isBinded);
}

void MainWindow::enableUpdateButton()
{
    ui->updateButton->setDisabled(false);
}

void MainWindow::updateConfig()
{

    disconnect(this, SLOT(appendMessage(QString, QString)));
    disconnect(this, SLOT(udpBinded(bool)));
    if (myudp)
    {
        myudp->unBind();
        delete myudp;
    }
    if (mytcpserver)
    {

    }

    targetAddr.setAddress(ui->lineEdit_targetIP->text());
    targetPort = ui->lineEdit_targetPort->text().toInt();
    localAddr.setAddress(ui->comboBox_localIP->currentText());

    setupConnection();

    saveSettings();
}

void MainWindow::findLocalIPs()
{
    QList<QNetworkInterface> listInterface = QNetworkInterface::allInterfaces();
    for (int i = 0; i < listInterface.size(); ++i)
    {
        if (listInterface.at(i).humanReadableName().contains("Wi-Fi"))
        {
            wifiList.append(listInterface.at(i));
        }
    }

    if (wifiList.isEmpty())
    {
        // TODO
    }
    else if (wifiList.size() == 1)
    {
        for (int i = 0; i < wifiList.at(0).addressEntries().size(); ++i)
        {
            if (wifiList.at(0).addressEntries().at(i).ip().protocol() == QAbstractSocket::IPv4Protocol)
            {
                ui->comboBox_localIP->addItem(wifiList.at(0).addressEntries().at(i).ip().toString());
                ui->comboBox_localIP->setDisabled(true);
                //qDebug() << wifiList.at(0).allAddresses().at(i).toString();
                //qDebug() << wifiList.at(0).humanReadableName();
            }
        }
    }
    else
    {
        // TODO comboBox_localIP index
    }
}

void MainWindow::disableComboBox(int index)
{
    ui->comboBox_serverClient->setDisabled(index == 1);
}

qint16 MainWindow::getProtocolValue()
{
    return ui->comboBox_TCPUDP->currentIndex();
}

qint16 MainWindow::getRoleValue()
{
    return ui->comboBox_serverClient->currentIndex();
}

void MainWindow::loadSettings()
{
    settingsFileDir = QApplication::applicationDirPath() + "/config.ini";
    QSettings settings(settingsFileDir, QSettings::IniFormat);
    ui->lineEdit_targetIP->setText(settings.value("targetIP", "127.0.0.1").toString());
    ui->lineEdit_targetPort->setText(settings.value("targetPort", 1234).toString());
    ui->lineEdit_listenPort->setText(settings.value("listenPort", 1234).toString());

    if (ui->comboBox_localIP->count() >= settings.value("localIPIndex", 0).toInt())
    {
        ui->comboBox_localIP->setCurrentIndex(settings.value("localIPIndex", 0).toInt());
    }

    ui->comboBox_TCPUDP->setCurrentIndex(settings.value("TCPorUDP", 0).toInt());
    ui->comboBox_serverClient->setCurrentIndex(settings.value("serverClient", 0).toInt());
    ui->comboBox_serverClient->setDisabled(settings.value("TCPorUDP", 0).toInt() == 1);
}

void MainWindow::saveSettings()
{
    QSettings settings(settingsFileDir, QSettings::IniFormat);
    settings.setValue("targetIP", ui->lineEdit_targetIP->text());
    settings.setValue("targetPort", ui->lineEdit_targetPort->text());
    settings.setValue("listenPort", ui->lineEdit_listenPort->text());
    settings.setValue("localIPIndex", ui->comboBox_localIP->currentIndex());
    settings.setValue("TCPorUDP", ui->comboBox_TCPUDP->currentIndex());
    settings.setValue("serverClient", ui->comboBox_serverClient->currentIndex());
    settings.sync();
}
