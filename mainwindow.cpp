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
            ui->startButton->setText("Start");
        }
        else if (getRoleValue() == CLIENT)
        {
            type = TCPCLIENT;
            ui->startButton->setText("Connect");
        }
    }
    else if (getProtocolValue() == UDP)
    {
        type = UDPSERVER;
        ui->startButton->setText("Start");
    }

    connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStartButtonClicked()));
    connect(ui->comboBox_TCPUDP, SIGNAL(currentIndexChanged(int)), this, SLOT(onTcpUdpComboChanged(int)));
    connect(ui->comboBox_serverClient, SIGNAL(currentIndexChanged(int)), this, SLOT(onServerClientComboChanged(int)));
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
        break;
    case TCPCLIENT:
        mytcpclient = new MyTCPClient;
        mytcpclient->connectTo(targetAddr, targetPort);
        temp = "TCP client is connecting to: ";
        appendMessage("System", temp.append(targetAddr.toString()).append(":").append(QString::number(targetPort)));
        isSuccess=true;
        break;
    case UDPSERVER:
        myudp = new MyUDP;
        connect(ui->pushButton_send, SIGNAL(clicked()), this, SLOT(sendMessage()));
        connect(ui->lineEdit_send, SIGNAL(returnPressed()), this, SLOT(sendMessage()));
        connect(myudp, SIGNAL(newMessage(QString, QString)), this, SLOT(appendMessage(QString, QString)));
        temp = "UDP socket is listening to: ";
        appendMessage("System", temp.append(QString::number(listenPort)));
        isSuccess = myudp->bindPort(localAddr, listenPort);
        break;
    }

    return isSuccess;
}

void MainWindow::onNewConnectionTcpServer(const QString &from, qint16 port)
{
    QString temp = "New connection from: ";
    appendMessage("System", temp.append(from).append(":").append(QString::number(port)));
    disconnect(mytcpserver, SIGNAL(myServerConnected(QString, qint16)), this, SLOT(onNewConnectionTcpServer(QString, qint16)));

    disconnect(ui->startButton, SIGNAL(clicked()), this, SLOT(onTcpStopButtonClicked()));
    ui->startButton->setText("Disconnect");
    connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onTcpDisconnectButtonClicked()));

    connect(mytcpserver, SIGNAL(myServerDisconnected()), this, SLOT(onDisconnectedTcpServer()));
    connect(mytcpserver, SIGNAL(newMessage(QString, QString)), this, SLOT(appendMessage(QString, QString)));

    ui->pushButton_send->setDisabled(false);
    ui->lineEdit_send->setDisabled(false);
    ui->textBrowser_message->setDisabled(false);
    connect(ui->pushButton_send, SIGNAL(clicked()), this, SLOT(sendMessage()));
    connect(ui->lineEdit_send, SIGNAL(returnPressed()), this, SLOT(sendMessage()));
}

void MainWindow::onDisconnectedTcpServer()
{
    appendMessage("System", "TCP disconnected");

    ui->pushButton_send->setDisabled(true);
    ui->lineEdit_send->setDisabled(true);
    ui->textBrowser_message->setDisabled(true);

    disconnect(ui->startButton, SIGNAL(clicked()), this, SLOT(onTcpDisconnectButtonClicked()));
    disconnect(mytcpserver, SIGNAL(myServerDisconnected()), this, SLOT(onDisconnectedTcpServer()));
    disconnect(mytcpserver, SIGNAL(newMessage(QString, QString)), this, SLOT(appendMessage(QString, QString)));
    disconnect(ui->pushButton_send, SIGNAL(clicked()), this, SLOT(sendMessage()));
    disconnect(ui->lineEdit_send, SIGNAL(returnPressed()), this, SLOT(sendMessage()));

    connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onTcpStopButtonClicked()));
    ui->startButton->setText("Stop");
    ui->startButton->setDisabled(false);
    connect(mytcpserver, SIGNAL(myServerConnected(QString, qint16)), this, SLOT(onNewConnectionTcpServer(QString, qint16)));
}

void MainWindow::onTcpDisconnectButtonClicked()
{
    qDebug() << "onTCPDisconnectButton";
    ui->startButton->setDisabled(true);
    if(type==TCPSERVER)
    {
        mytcpserver->disconnectCurrentConnection();
    }
    else if(type==TCPCLIENT)
    {
        mytcpclient->disconnectCurrentConnection();
    }
}

void MainWindow::onNewConnectionTcpClient(const QString &from, qint16 port)
{
    disconnect(mytcpclient, SIGNAL(myClientConnected(QString, qint16)), this, SLOT(onNewConnectionTcpClient(QString, qint16)));
    disconnect(mytcpclient,SIGNAL(connectionFailed()),this,SLOT(onTimeOutTcpClient()));
    connect(mytcpclient, SIGNAL(myClientDisconnected()), this, SLOT(onDisconnectedTcpClient()));

    ui->startButton->setDisabled(false);
    ui->startButton->setText("Disconnect");

    ui->pushButton_send->setDisabled(false);
    ui->lineEdit_send->setDisabled(false);
    ui->textBrowser_message->setDisabled(false);

    QString temp = "Connected to: ";
    appendMessage("System", temp.append(from).append(":").append(QString::number(port)));
    connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onTcpDisconnectButtonClicked()));

    connect(mytcpclient, SIGNAL(newMessage(QString, QString)), this, SLOT(appendMessage(QString, QString)));
    connect(ui->pushButton_send, SIGNAL(clicked()), this, SLOT(sendMessage()));
    connect(ui->lineEdit_send, SIGNAL(returnPressed()), this, SLOT(sendMessage()));
}

void MainWindow::onDisconnectedTcpClient()
{
    disconnect(mytcpclient, SIGNAL(myClientDisconnected()), this, SLOT(onDisconnectedTcpClient()));
    disconnect(mytcpclient, SIGNAL(newMessage(QString, QString)), this, SLOT(appendMessage(QString, QString)));
    disconnect(ui->pushButton_send, SIGNAL(clicked()), this, SLOT(sendMessage()));
    disconnect(ui->lineEdit_send, SIGNAL(returnPressed()), this, SLOT(sendMessage()));
    disconnect(ui->startButton, SIGNAL(clicked()), this, SLOT(onTcpDisconnectButtonClicked()));
    ui->startButton->setText("Connect");

    ui->pushButton_send->setDisabled(true);
    ui->lineEdit_send->setDisabled(true);
    ui->textBrowser_message->setDisabled(true);

    ui->startButton->setDisabled(false);
    ui->comboBox_TCPUDP->setDisabled(false);
    ui->comboBox_serverClient->setDisabled(false);
    ui->lineEdit_targetIP->setDisabled(false);
    ui->lineEdit_targetPort->setDisabled(false);
    ui->lineEdit_listenPort->setDisabled(false);

    mytcpclient->cleanClient();
    mytcpclient->close();
    mytcpclient->deleteLater();
    mytcpclient=nullptr;

    connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStartButtonClicked()));
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

    appendMessage("Me", text);
    ui->lineEdit_send->clear();
}

void MainWindow::onStartButtonClicked()
{
    disconnect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStartButtonClicked()));

    if (setupConnection())
    {
        if (type == UDPSERVER)
        {
            connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onUdpStopButtonClicked()));
            ui->startButton->setText("Stop");

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
            connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onTcpStopButtonClicked()));
            ui->startButton->setText("Stop");

            ui->comboBox_TCPUDP->setDisabled(true);
            ui->comboBox_serverClient->setDisabled(true);
            ui->lineEdit_targetIP->setDisabled(true);
            ui->lineEdit_targetPort->setDisabled(true);
            ui->lineEdit_listenPort->setDisabled(true);
            connect(mytcpserver, SIGNAL(myServerConnected(QString, qint16)), this, SLOT(onNewConnectionTcpServer(QString, qint16)));
            //connect(mytcpserver, SIGNAL(myServerDisconnected()), this, SLOT(TCPServerDisconnected()));
        }
        else if (type == TCPCLIENT)
        {
            ui->comboBox_TCPUDP->setDisabled(true);
            ui->comboBox_serverClient->setDisabled(true);
            ui->lineEdit_targetIP->setDisabled(true);
            ui->lineEdit_targetPort->setDisabled(true);
            ui->lineEdit_listenPort->setDisabled(true);
            //connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onDisconnectButton()));
            connect(mytcpclient, SIGNAL(myClientConnected(QString, qint16)), this, SLOT(onNewConnectionTcpClient(QString, qint16)));
            connect(mytcpclient,SIGNAL(connectionFailed()),this,SLOT(onTimeOutTcpClient()));
        }
    }
    else
    {
        connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStartButtonClicked()));
    }
    saveSettings();
}

void MainWindow::onTimeOutTcpClient()
{
    disconnect(mytcpclient, SIGNAL(myClientConnected(QString, qint16)), this, SLOT(onNewConnectionTcpClient(QString, qint16)));
    disconnect(mytcpclient,SIGNAL(connectionFailed()),this,SLOT(onTimeOutTcpClient()));
    ui->startButton->setDisabled(false);
    ui->comboBox_TCPUDP->setDisabled(false);
    ui->comboBox_serverClient->setDisabled(false);
    ui->lineEdit_targetIP->setDisabled(false);
    ui->lineEdit_targetPort->setDisabled(false);
    ui->lineEdit_listenPort->setDisabled(false);
    mytcpclient->cleanClient();
    mytcpclient->close();
    mytcpclient->deleteLater();
    mytcpclient=nullptr;
    connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStartButtonClicked()));
}

void MainWindow::onUdpStopButtonClicked()
{
    disconnect(ui->startButton, SIGNAL(clicked()), this, SLOT(onUdpStopButtonClicked()));
    ui->startButton->setText("Start");
    ui->pushButton_send->setDisabled(true);
    ui->lineEdit_send->setDisabled(true);
    ui->textBrowser_message->setDisabled(true);

    ui->comboBox_TCPUDP->setDisabled(false);

    ui->lineEdit_targetIP->setDisabled(false);
    ui->lineEdit_targetPort->setDisabled(false);
    ui->lineEdit_listenPort->setDisabled(false);
    if (type != UDPSERVER)
    {
        ui->comboBox_serverClient->setDisabled(false);
    }

    if (myudp != nullptr)
    {
        myudp->unBind();
        myudp = nullptr;
    }

    connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStartButtonClicked()));
}

void MainWindow::onTcpStopButtonClicked()
{
    disconnect(mytcpserver, SIGNAL(myServerConnected(QString, qint16)));
    qDebug() << "disconnect(mytcpserver, SIGNAL(myServerConnected(QString, qint16)));";
    disconnect(ui->startButton, SIGNAL(clicked()), this, SLOT(onTcpStopButtonClicked()));
    qDebug() << "disconnect(ui->startButton, SIGNAL(clicked()), this, SLOT(onTCPCancelButton()));";
    ui->startButton->setText("Start");
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

    connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStartButtonClicked()));
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

quint8 MainWindow::getProtocolValue()
{
    return ui->comboBox_TCPUDP->currentIndex();
}

quint8 MainWindow::getRoleValue()
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

void MainWindow::onTcpUdpComboChanged(int index)
{
    int tcptype = getRoleValue();
    switch (index)
    {
    case TCP:
        if (tcptype == SERVER)
        {
            type = TCPSERVER;
            ui->startButton->setText("Start");
        }
        else if (tcptype == CLIENT)
        {
            type = TCPCLIENT;
            ui->startButton->setText("Connect");
        }
        ui->comboBox_serverClient->setDisabled(false);
        break;
    case UDP:
        type = UDPSERVER;
        ui->startButton->setText("Start");
        ui->comboBox_serverClient->setDisabled(true);
        break;
    }
}

void MainWindow::onServerClientComboChanged(int index)
{
    switch (index)
    {
    case SERVER:
        type = TCPSERVER;
        ui->startButton->setText("Start");
        break;
    case CLIENT:
        type = TCPCLIENT;
        ui->startButton->setText("Connect");
        break;
    }
}
