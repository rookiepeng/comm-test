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

    if (getProtocolValue() == TCP)
    {
        if (getRoleValue() == SERVER)
        {
            type = TCPSERVER;
            ui->connectButton->setText("Listen");
        }
        else if (getRoleValue() == CLIENT)
        {
            type = TCPCLIENT;
            ui->connectButton->setText("Connect");
        }
    }
    else if (getProtocolValue() == UDP)
    {
        type = UDPSERVER;
        ui->connectButton->setText("Listen");
    }

    connect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onConnectButton()));
    connect(ui->comboBox_TCPUDP, SIGNAL(currentIndexChanged(int)), this, SLOT(TCPUDPComboChanged(int)));
    connect(ui->comboBox_serverClient, SIGNAL(currentIndexChanged(int)), this, SLOT(ServerClientComboChanged(int)));

    //setupConnection();
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

    ui->pushButton_send->setDisabled(true);
    ui->lineEdit_send->setDisabled(true);
    ui->textBrowser_message->setDisabled(true);

    tableFormat.setBorder(0);

    connect(ui->comboBox_TCPUDP, SIGNAL(currentIndexChanged(int)), this, SLOT(disableComboBox(int)));
}

bool MainWindow::setupConnection()
{
    bool isSuccess;
    QString temp;
    targetAddr.setAddress(ui->lineEdit_targetIP->text());
    targetPort = ui->lineEdit_targetPort->text().toInt();
    localAddr.setAddress(ui->comboBox_localIP->currentText());
    listenPort = ui->lineEdit_listenPort->text().toInt();

    switch (type)
    {
    case TCPSERVER:
        mytcpserver = new MyTCPServer;
        isSuccess = mytcpserver->listen(localAddr, listenPort);
        temp = "TCP server is listening to port: ";
        appendMessage("System", temp.append(QString::number(listenPort)));
        //connect(mytcpserver, SIGNAL(myServerConnected(QString, qint16)), this, SLOT(newTCPServerConnection(QString, qint16)));
        //connect(mytcpserver, SIGNAL(myServerDisconnected()), this, SLOT(TCPServerDisconnected()));
        break;
    case TCPCLIENT:
        mytcpclient = new MyTCPClient;
        mytcpclient->connectTo(targetAddr, targetPort);
        temp = "TCP client is connecting to: ";
        appendMessage("System", temp.append(targetAddr.toString()).append(":").append(QString::number(targetPort)));
        //connect(mytcpclient, SIGNAL(myClientConnected(QString, qint16)), this, SLOT(newTCPClientConnection(QString, qint16)));
        //connect(mytcpclient, SIGNAL(myClientDisconnected()), this, SLOT(TCPClientDisconnected()));
        isSuccess=true;
        break;
    case UDPSERVER:
        myudp = new MyUDP;
        connect(ui->pushButton_send, SIGNAL(clicked()), this, SLOT(sendMessage()));
        connect(ui->lineEdit_send, SIGNAL(returnPressed()), this, SLOT(sendMessage()));
        connect(myudp, SIGNAL(newMessage(QString, QString)), this, SLOT(appendMessage(QString, QString)));
        //connect(myudp, SIGNAL(bindSuccess(bool)), this, SLOT(udpBinded(bool)));
        temp = "UDP socket is listening to: ";
        appendMessage("System", temp.append(QString::number(listenPort)));
        isSuccess = myudp->bindPort(localAddr, listenPort);
        break;
    }

    return isSuccess;
}

void MainWindow::newTCPServerConnection(const QString &from, qint16 port)
{
    QString temp = "New connection from: ";
    appendMessage("System", temp.append(from).append(":").append(QString::number(port)));
    disconnect(mytcpserver, SIGNAL(myServerConnected(QString, qint16)), this, SLOT(newTCPServerConnection(QString, qint16)));

    disconnect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onTCPCancelButton()));
    ui->connectButton->setText("Disconnect");
    connect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onTCPDisconnectButton()));

    connect(mytcpserver, SIGNAL(myServerDisconnected()), this, SLOT(TCPServerDisconnected()));
    connect(mytcpserver, SIGNAL(newMessage(QString, QString)), this, SLOT(appendMessage(QString, QString)));

    ui->pushButton_send->setDisabled(false);
    ui->lineEdit_send->setDisabled(false);
    ui->textBrowser_message->setDisabled(false);
    connect(ui->pushButton_send, SIGNAL(clicked()), this, SLOT(sendMessage()));
    connect(ui->lineEdit_send, SIGNAL(returnPressed()), this, SLOT(sendMessage()));
}

void MainWindow::TCPServerDisconnected()
{
    appendMessage("System", "TCP disconnected");

    ui->pushButton_send->setDisabled(true);
    ui->lineEdit_send->setDisabled(true);
    ui->textBrowser_message->setDisabled(true);

    //disconnect(ui->connectButton, SIGNAL(clicked()));
    disconnect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onTCPDisconnectButton()));
    disconnect(mytcpserver, SIGNAL(myServerDisconnected()), this, SLOT(TCPServerDisconnected()));
    disconnect(mytcpserver, SIGNAL(newMessage(QString, QString)), this, SLOT(appendMessage(QString, QString)));
    disconnect(ui->pushButton_send, SIGNAL(clicked()), this, SLOT(sendMessage()));
    disconnect(ui->lineEdit_send, SIGNAL(returnPressed()), this, SLOT(sendMessage()));

    connect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onTCPCancelButton()));
    ui->connectButton->setText("Cancel");
    ui->connectButton->setDisabled(false);
    connect(mytcpserver, SIGNAL(myServerConnected(QString, qint16)), this, SLOT(newTCPServerConnection(QString, qint16)));
}

void MainWindow::onTCPDisconnectButton()
{
    qDebug() << "onTCPDisconnectButton";
    ui->connectButton->setDisabled(true);
    //disconnect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onTCPDisconnectButton()));
    if(type==TCPSERVER)
    {
        mytcpserver->disconnectCurrentConnection();
    }
    else if(type==TCPCLIENT)
    {
        mytcpclient->disconnectCurrentConnection();
    }
}

void MainWindow::newTCPClientConnection(const QString &from, qint16 port)
{
    disconnect(mytcpclient, SIGNAL(myClientConnected(QString, qint16)), this, SLOT(newTCPClientConnection(QString, qint16)));
    disconnect(mytcpclient,SIGNAL(connectionFailed()),this,SLOT(tcpClientTimeOut()));
    connect(mytcpclient, SIGNAL(myClientDisconnected()), this, SLOT(TCPClientDisconnected()));

    ui->connectButton->setDisabled(false);
    ui->connectButton->setText("Disconnect");
    //connect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onTCPCancelButton()));

    ui->pushButton_send->setDisabled(false);
    ui->lineEdit_send->setDisabled(false);
    ui->textBrowser_message->setDisabled(false);

    QString temp = "Connected to: ";
    appendMessage("System", temp.append(from).append(":").append(QString::number(port)));
    connect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onTCPDisconnectButton()));

    connect(mytcpclient, SIGNAL(newMessage(QString, QString)), this, SLOT(appendMessage(QString, QString)));
    connect(ui->pushButton_send, SIGNAL(clicked()), this, SLOT(sendMessage()));
    connect(ui->lineEdit_send, SIGNAL(returnPressed()), this, SLOT(sendMessage()));
}

void MainWindow::TCPClientDisconnected()
{
    disconnect(mytcpclient, SIGNAL(myClientDisconnected()), this, SLOT(TCPClientDisconnected()));
    disconnect(mytcpclient, SIGNAL(newMessage(QString, QString)), this, SLOT(appendMessage(QString, QString)));
    disconnect(ui->pushButton_send, SIGNAL(clicked()), this, SLOT(sendMessage()));
    disconnect(ui->lineEdit_send, SIGNAL(returnPressed()), this, SLOT(sendMessage()));
    disconnect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onTCPDisconnectButton()));
    ui->connectButton->setText("Connect");

    ui->pushButton_send->setDisabled(true);
    ui->lineEdit_send->setDisabled(true);
    ui->textBrowser_message->setDisabled(true);

    ui->connectButton->setDisabled(false);
    ui->comboBox_TCPUDP->setDisabled(false);
    ui->comboBox_serverClient->setDisabled(false);
    ui->lineEdit_targetIP->setDisabled(false);
    ui->lineEdit_targetPort->setDisabled(false);
    ui->lineEdit_listenPort->setDisabled(false);

    mytcpclient->cleanClient();
    mytcpclient->close();
    mytcpclient->deleteLater();
    mytcpclient=nullptr;

    connect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onConnectButton()));
}

void MainWindow::appendMessage(const QString &from, const QString &message)
{
    if (from.isEmpty() || message.isEmpty())
    {
        return;
    }

    QTextCursor cursor(ui->textBrowser_message->textCursor());
    cursor.movePosition(QTextCursor::End);

    if (from == "System")
    {
        QColor color = ui->textBrowser_message->textColor();
        ui->textBrowser_message->setTextColor(Qt::gray);
        ui->textBrowser_message->append(message);
        ui->textBrowser_message->setTextColor(color);
    }
    else
    {
        QTextTable *table = cursor.insertTable(1, 2, tableFormat);
        table->cellAt(0, 0).firstCursorPosition().insertText('<' + from + "> ");
        table->cellAt(0, 1).firstCursorPosition().insertText(message);
    }
    QScrollBar *bar = ui->textBrowser_message->verticalScrollBar();
    bar->setValue(bar->maximum());
}

void MainWindow::sendMessage()
{
    QString text = ui->lineEdit_send->text();
    if (text.isEmpty())
    {
        return;
    }

    if (getProtocolValue() == TCP)
    {
        if (getRoleValue() == SERVER)
        {
            mytcpserver->sendMessage(text);
        }
        else if (getRoleValue() == CLIENT)
        {
            mytcpclient->sendMessage(text);
        }
    }
    else if (getProtocolValue() == UDP)
    {
        myudp->sendMessage(targetAddr, targetPort, text);
    }

    appendMessage("client", text);
    ui->lineEdit_send->clear();
}

void MainWindow::udpBinded(bool isBinded)
{
    ui->connectButton->setDisabled(isBinded);
}

void MainWindow::enableUpdateButton()
{
    ui->connectButton->setDisabled(false);
}

void MainWindow::onConnectButton()
{
    disconnect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onConnectButton()));
    ui->connectButton->setDisabled(true);
    //disconnect(ui->pushButton_send, SIGNAL(clicked()), this, SLOT(sendMessage()));
    //disconnect(ui->lineEdit_send, SIGNAL(returnPressed()), this, SLOT(sendMessage()));

    if (setupConnection())
    {
        if (type == UDPSERVER)
        {
            connect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onUDPCancelButton()));
            ui->connectButton->setText("Cancel");
            ui->connectButton->setDisabled(false);

            ui->pushButton_send->setDisabled(false);
            ui->lineEdit_send->setDisabled(false);
            ui->textBrowser_message->setDisabled(false);

            ui->comboBox_TCPUDP->setDisabled(true);
            ui->comboBox_serverClient->setDisabled(true);
            ui->lineEdit_targetIP->setDisabled(true);
            ui->lineEdit_targetPort->setDisabled(true);
            ui->lineEdit_listenPort->setDisabled(true);
        }
        else if (type == TCPSERVER)
        {
            connect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onTCPCancelButton()));
            ui->connectButton->setText("Cancel");
            ui->connectButton->setDisabled(false);

            //ui->pushButton_send->setDisabled(false);
            //ui->lineEdit_send->setDisabled(false);
            //ui->textBrowser_message->setDisabled(false);

            ui->comboBox_TCPUDP->setDisabled(true);
            ui->comboBox_serverClient->setDisabled(true);
            ui->lineEdit_targetIP->setDisabled(true);
            ui->lineEdit_targetPort->setDisabled(true);
            ui->lineEdit_listenPort->setDisabled(true);
            connect(mytcpserver, SIGNAL(myServerConnected(QString, qint16)), this, SLOT(newTCPServerConnection(QString, qint16)));
            //connect(mytcpserver, SIGNAL(myServerDisconnected()), this, SLOT(TCPServerDisconnected()));
        }
        else if (type == TCPCLIENT)
        {
            ui->connectButton->setDisabled(true);
            ui->comboBox_TCPUDP->setDisabled(true);
            ui->comboBox_serverClient->setDisabled(true);
            ui->lineEdit_targetIP->setDisabled(true);
            ui->lineEdit_targetPort->setDisabled(true);
            ui->lineEdit_listenPort->setDisabled(true);
            //connect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onDisconnectButton()));
            connect(mytcpclient, SIGNAL(myClientConnected(QString, qint16)), this, SLOT(newTCPClientConnection(QString, qint16)));
            connect(mytcpclient,SIGNAL(connectionFailed()),this,SLOT(tcpClientTimeOut()));
        }
    }
    else
    {
        ui->connectButton->setDisabled(false);
        connect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onConnectButton()));
    }

    saveSettings();
}

void MainWindow::tcpClientTimeOut()
{
    disconnect(mytcpclient, SIGNAL(myClientConnected(QString, qint16)), this, SLOT(newTCPClientConnection(QString, qint16)));
    disconnect(mytcpclient,SIGNAL(connectionFailed()),this,SLOT(tcpClientTimeOut()));
    ui->connectButton->setDisabled(false);
    ui->comboBox_TCPUDP->setDisabled(false);
    ui->comboBox_serverClient->setDisabled(false);
    ui->lineEdit_targetIP->setDisabled(false);
    ui->lineEdit_targetPort->setDisabled(false);
    ui->lineEdit_listenPort->setDisabled(false);
    mytcpclient->cleanClient();
    mytcpclient->close();
    mytcpclient->deleteLater();
    mytcpclient=nullptr;
    connect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onConnectButton()));
}

void MainWindow::onUDPCancelButton()
{
    disconnect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onUDPCancelButton()));
    ui->connectButton->setText("Listen");
    ui->pushButton_send->setDisabled(true);
    ui->lineEdit_send->setDisabled(true);
    ui->textBrowser_message->setDisabled(true);

    ui->comboBox_TCPUDP->setDisabled(false);
    //ui->comboBox_serverClient->setDisabled(false);
    ui->lineEdit_targetIP->setDisabled(false);
    ui->lineEdit_targetPort->setDisabled(false);
    ui->lineEdit_listenPort->setDisabled(false);
    if (type != UDPSERVER)
    {
        ui->comboBox_serverClient->setDisabled(false);
    }

    if (myudp != nullptr)
    {
        qDebug() << "Delete UDP";
        //disconnect(this, SLOT(sendMessage()));
        disconnect(this, SLOT(udpBinded(bool)));

        myudp->unBind();
        //delete myudp;
        myudp = nullptr;
    }
    //    if (mytcpserver != nullptr)
    //    {
    //        qDebug() << "Delete TCP Server";
    //        mytcpserver->close();
    //        mytcpserver->deleteLater();
    //        mytcpserver = nullptr;
    //    }
    //    if (mytcpclient != nullptr)
    //    {
    //        qDebug() << "Delete TCP Client";
    //        mytcpclient->close();
    //        mytcpclient->deleteLater();
    //        mytcpclient = nullptr;
    //    }
    connect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onConnectButton()));
}

void MainWindow::onTCPCancelButton()
{
    disconnect(mytcpserver, SIGNAL(myServerConnected(QString, qint16)));
    qDebug() << "disconnect(mytcpserver, SIGNAL(myServerConnected(QString, qint16)));";
    disconnect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onTCPCancelButton()));
    qDebug() << "disconnect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onTCPCancelButton()));";
    ui->connectButton->setText("Listen");
    ui->pushButton_send->setDisabled(true);
    ui->lineEdit_send->setDisabled(true);
    ui->textBrowser_message->setDisabled(true);

    ui->comboBox_TCPUDP->setDisabled(false);
    //ui->comboBox_serverClient->setDisabled(false);
    ui->lineEdit_targetIP->setDisabled(false);
    ui->lineEdit_targetPort->setDisabled(false);
    ui->lineEdit_listenPort->setDisabled(false);
    if (type != UDPSERVER)
    {
        ui->comboBox_serverClient->setDisabled(false);
    }

    if (mytcpserver != nullptr)
    {
        qDebug() << "Delete TCP Server";
        mytcpserver->close();
        mytcpserver->deleteLater();
        mytcpserver = nullptr;
    }

    connect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onConnectButton()));
}

void MainWindow::onDisconnectButton()
{
    disconnect(ui->connectButton, SIGNAL(clicked()), this, SLOT(onDisconnectButton()));
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

void MainWindow::TCPUDPComboChanged(int index)
{
    int tcptype = getRoleValue();
    switch (index)
    {
    case TCP:
        if (tcptype == SERVER)
        {
            type = TCPSERVER;
            ui->connectButton->setText("Listen");
        }
        else if (tcptype == CLIENT)
        {
            type = TCPCLIENT;
            ui->connectButton->setText("Connect");
        }
        ui->comboBox_serverClient->setDisabled(false);
        break;
    case UDP:
        type = UDPSERVER;
        ui->connectButton->setText("Listen");
        ui->comboBox_serverClient->setDisabled(true);
        break;
    }
}

void MainWindow::ServerClientComboChanged(int index)
{
    switch (index)
    {
    case SERVER:
        type = TCPSERVER;
        ui->connectButton->setText("Listen");
        break;
    case CLIENT:
        type = TCPCLIENT;
        ui->connectButton->setText("Connect");
        break;
    }
}
