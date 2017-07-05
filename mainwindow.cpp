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

    targetIPString = ui->lineEdit_targetIP->text();
    targetPortString = ui->lineEdit_targetPort->text();
    listenPortString = ui->lineEdit_listenPort->text();

    if (getProtocolValue() == TCP)
    {
        if (getRoleValue() == SERVER)
        {
            type = TCPSERVER;
            ui->startButton->setText("Start");

            ui->lineEdit_targetIP->clear();
            ui->lineEdit_targetIP->setDisabled(true);
            ui->lineEdit_targetPort->clear();
            ui->lineEdit_targetPort->setDisabled(true);
        }
        else if (getRoleValue() == CLIENT)
        {
            type = TCPCLIENT;
            ui->startButton->setText("Connect");

            ui->lineEdit_listenPort->clear();
            ui->lineEdit_listenPort->setDisabled(true);
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

/*
 * UI initialization
 */
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

/*
 * Setup connections
 */
bool MainWindow::setupConnection()
{
    bool isSuccess = false;
    targetAddr.setAddress(ui->lineEdit_targetIP->text());
    targetPort = ui->lineEdit_targetPort->text().toInt();
    localAddr.setAddress(ui->comboBox_localIP->currentText());
    listenPort = ui->lineEdit_listenPort->text().toInt();

    switch (type)
    {
    case TCPSERVER:
        if (mytcpserver == nullptr)
        {
            mytcpserver = new MyTCPServer;
        }
        isSuccess = mytcpserver->listen(localAddr, listenPort);
        break;
    case TCPCLIENT:
        if (mytcpclient == nullptr)
        {
            mytcpclient = new MyTCPClient;
        }
        mytcpclient->connectTo(targetAddr, targetPort);
        isSuccess = true;
        break;
    case UDPSERVER:
        if (myudp == nullptr)
        {
            myudp = new MyUDP;
        }
        isSuccess = myudp->bindPort(localAddr, listenPort);
        break;
    }
    return isSuccess;
}

/*
 * TCP server has a new connection
 */
void MainWindow::onNewConnectionTcpServer(const QString &from, quint16 port)
{
    ui->statusBar->showMessage(messageTCP + "Connected with " + from + ": " + QString::number(port), 0);
    disconnect(mytcpserver, SIGNAL(myServerConnected(QString, quint16)), this, SLOT(onNewConnectionTcpServer(QString, quint16)));

    disconnect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStopButtonClicked()));
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

/*
 * TCP server disconnected
 */
void MainWindow::onDisconnectedTcpServer()
{
    ui->statusBar->showMessage(messageTCP + "Client disconnected, listerning to " + localAddr.toString() + ": " + QString::number(listenPort), 0);

    ui->pushButton_send->setDisabled(true);
    ui->lineEdit_send->setDisabled(true);
    ui->textBrowser_message->setDisabled(true);

    disconnect(ui->startButton, SIGNAL(clicked()), this, SLOT(onTcpDisconnectButtonClicked()));
    disconnect(mytcpserver, SIGNAL(myServerDisconnected()), this, SLOT(onDisconnectedTcpServer()));
    disconnect(mytcpserver, SIGNAL(newMessage(QString, QString)), this, SLOT(appendMessage(QString, QString)));
    disconnect(ui->pushButton_send, SIGNAL(clicked()), this, SLOT(sendMessage()));
    disconnect(ui->lineEdit_send, SIGNAL(returnPressed()), this, SLOT(sendMessage()));

    connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStopButtonClicked()));
    ui->startButton->setText("Stop");
    connect(mytcpserver, SIGNAL(myServerConnected(QString, quint16)), this, SLOT(onNewConnectionTcpServer(QString, quint16)));
}

/*
 * Disconnet button clicked
 */
void MainWindow::onTcpDisconnectButtonClicked()
{
    if (type == TCPSERVER)
    {
        mytcpserver->stopConnection();
    }
    else if (type == TCPCLIENT)
    {
        mytcpclient->disconnectCurrentConnection();
    }
}

/*
 * TCP client has a new connection
 */
void MainWindow::onNewConnectionTcpClient(const QString &from, quint16 port)
{
    disconnect(mytcpclient, SIGNAL(myClientConnected(QString, quint16)), this, SLOT(onNewConnectionTcpClient(QString, quint16)));
    disconnect(mytcpclient, SIGNAL(connectionFailed()), this, SLOT(onTimeOutTcpClient()));
    disconnect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStopButtonClicked()));
    connect(mytcpclient, SIGNAL(myClientDisconnected()), this, SLOT(onDisconnectedTcpClient()));

    ui->startButton->setDisabled(false);
    ui->startButton->setText("Disconnect");

    ui->pushButton_send->setDisabled(false);
    ui->lineEdit_send->setDisabled(false);
    ui->textBrowser_message->setDisabled(false);

    ui->statusBar->showMessage(messageTCP + "Connected to " + from + ": " + QString::number(port), 0);
    connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onTcpDisconnectButtonClicked()));

    connect(mytcpclient, SIGNAL(newMessage(QString, QString)), this, SLOT(appendMessage(QString, QString)));
    connect(ui->pushButton_send, SIGNAL(clicked()), this, SLOT(sendMessage()));
    connect(ui->lineEdit_send, SIGNAL(returnPressed()), this, SLOT(sendMessage()));
}

/*
 * TCP client disconnected
 */
void MainWindow::onDisconnectedTcpClient()
{
    ui->statusBar->showMessage(messageTCP + "Disconnected from server", 2000);
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

    mytcpclient->closeClient();
    mytcpclient->close();

    connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStartButtonClicked()));
}

/*
 * Append message to the message browser
 */
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

/*
 * Send message through Sockets
 */
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

/*
 * The start button clicked
 */
void MainWindow::onStartButtonClicked()
{
    disconnect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStartButtonClicked()));

    if (setupConnection())
    {
        if (type == UDPSERVER)
        {
            ui->statusBar->showMessage(messageUDP + "Listerning to " + localAddr.toString() + ": " + QString::number(listenPort), 0);
            connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStopButtonClicked()));
            ui->startButton->setText("Stop");

            ui->pushButton_send->setDisabled(false);
            ui->lineEdit_send->setDisabled(false);
            ui->textBrowser_message->setDisabled(false);

            ui->comboBox_TCPUDP->setDisabled(true);
            ui->comboBox_serverClient->setDisabled(true);
            ui->lineEdit_targetIP->setDisabled(true);
            ui->lineEdit_targetPort->setDisabled(true);
            ui->lineEdit_listenPort->setDisabled(true);
            connect(ui->pushButton_send, SIGNAL(clicked()), this, SLOT(sendMessage()));
            connect(ui->lineEdit_send, SIGNAL(returnPressed()), this, SLOT(sendMessage()));
            connect(myudp, SIGNAL(newMessage(QString, QString)), this, SLOT(appendMessage(QString, QString)));
        }
        else if (type == TCPSERVER)
        {
            ui->statusBar->showMessage(messageTCP + "Listerning to " + localAddr.toString() + ": " + QString::number(listenPort), 0);
            connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStopButtonClicked()));
            ui->startButton->setText("Stop");

            ui->comboBox_TCPUDP->setDisabled(true);
            ui->comboBox_serverClient->setDisabled(true);
            ui->lineEdit_targetIP->setDisabled(true);
            ui->lineEdit_targetPort->setDisabled(true);
            ui->lineEdit_listenPort->setDisabled(true);
            connect(mytcpserver, SIGNAL(myServerConnected(QString, quint16)), this, SLOT(onNewConnectionTcpServer(QString, quint16)));
        }
        else if (type == TCPCLIENT)
        {
            ui->statusBar->showMessage(messageTCP + "Connecting to " + targetAddr.toString() + ": " + QString::number(targetPort), 0);
            ui->comboBox_TCPUDP->setDisabled(true);
            ui->comboBox_serverClient->setDisabled(true);
            ui->lineEdit_targetIP->setDisabled(true);
            ui->lineEdit_targetPort->setDisabled(true);
            ui->lineEdit_listenPort->setDisabled(true);
            ui->startButton->setText("Stop");
            connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStopButtonClicked()));
            connect(mytcpclient, SIGNAL(myClientConnected(QString, quint16)), this, SLOT(onNewConnectionTcpClient(QString, quint16)));
            connect(mytcpclient, SIGNAL(connectionFailed()), this, SLOT(onTimeOutTcpClient()));
        }
    }
    else if (type == TCPSERVER)
    {
        ui->statusBar->showMessage(messageTCP + "Failed to listen to: " + localAddr.toString() + ": " + QString::number(listenPort), 2000);
        connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStartButtonClicked()));
    }
    else if (type == UDPSERVER)
    {
        ui->statusBar->showMessage(messageUDP + "Failed to listen to: " + localAddr.toString() + ": " + QString::number(listenPort), 2000);
        connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStartButtonClicked()));
    }
    saveSettings();
}

/*
 * TCP client connection time out
 */
void MainWindow::onTimeOutTcpClient()
{
    ui->statusBar->showMessage(messageTCP + "Connection time out", 2000);
    disconnect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStopButtonClicked()));
    disconnect(mytcpclient, SIGNAL(myClientConnected(QString, quint16)), this, SLOT(onNewConnectionTcpClient(QString, quint16)));
    disconnect(mytcpclient, SIGNAL(connectionFailed()), this, SLOT(onTimeOutTcpClient()));

    ui->startButton->setText("Connect");
    ui->comboBox_TCPUDP->setDisabled(false);
    ui->comboBox_serverClient->setDisabled(false);
    ui->lineEdit_targetIP->setDisabled(false);
    ui->lineEdit_targetPort->setDisabled(false);

    mytcpclient->closeClient();
    connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStartButtonClicked()));
}

/*
 * The stop button clicked
 */
void MainWindow::onStopButtonClicked()
{
    disconnect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStopButtonClicked()));

    if (type == TCPSERVER)
    {
        ui->statusBar->showMessage(messageTCP + "Stopped", 2000);
        disconnect(mytcpserver, SIGNAL(myServerConnected(QString, quint16)));
        mytcpserver->stopListening();
        ui->startButton->setText("Start");
        ui->comboBox_serverClient->setDisabled(false);
        ui->lineEdit_listenPort->setDisabled(false);
    }
    else if (type == TCPCLIENT)
    {
        ui->statusBar->showMessage(messageTCP + "Stopped", 2000);
        disconnect(mytcpclient, SIGNAL(myClientConnected(QString, quint16)), this, SLOT(onNewConnectionTcpClient(QString, quint16)));
        disconnect(mytcpclient, SIGNAL(connectionFailed()), this, SLOT(onTimeOutTcpClient()));
        ui->startButton->setText("Connect");
        mytcpclient->abortConnection();
        ui->comboBox_serverClient->setDisabled(false);
        ui->lineEdit_targetIP->setDisabled(false);
        ui->lineEdit_targetPort->setDisabled(false);
    }
    else if (type == UDPSERVER)
    {
        ui->statusBar->showMessage(messageUDP + "Stopped", 2000);
        disconnect(ui->pushButton_send, SIGNAL(clicked()), this, SLOT(sendMessage()));
        disconnect(ui->lineEdit_send, SIGNAL(returnPressed()), this, SLOT(sendMessage()));
        disconnect(myudp, SIGNAL(newMessage(QString, QString)), this, SLOT(appendMessage(QString, QString)));
        ui->startButton->setText("Start");
        myudp->unbindPort();
        ui->lineEdit_targetIP->setDisabled(false);
        ui->lineEdit_targetPort->setDisabled(false);
        ui->lineEdit_listenPort->setDisabled(false);
    }

    ui->pushButton_send->setDisabled(true);
    ui->lineEdit_send->setDisabled(true);
    ui->textBrowser_message->setDisabled(true);

    ui->comboBox_TCPUDP->setDisabled(false);

    connect(ui->startButton, SIGNAL(clicked()), this, SLOT(onStartButtonClicked()));
}

/*
 * Find IP of local WiFi connections
 */
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
                //ui->comboBox_localIP->setDisabled(true);
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

/*
 * Get current protocol selection
 */
quint8 MainWindow::getProtocolValue()
{
    return ui->comboBox_TCPUDP->currentIndex();
}

/*
 * Get current TCP role selection
 */
quint8 MainWindow::getRoleValue()
{
    return ui->comboBox_serverClient->currentIndex();
}

/*
 * Load settings from local configuration file
 */
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

/*
 * Save settings to local configuration file
 */
void MainWindow::saveSettings()
{
    QSettings settings(settingsFileDir, QSettings::IniFormat);
    settings.setValue("targetIP", targetIPString);
    settings.setValue("targetPort", targetPortString);
    settings.setValue("listenPort", listenPortString);
    settings.setValue("localIPIndex", ui->comboBox_localIP->currentIndex());
    settings.setValue("TCPorUDP", ui->comboBox_TCPUDP->currentIndex());
    settings.setValue("serverClient", ui->comboBox_serverClient->currentIndex());
    settings.sync();
}

/*
 * When TCP/UDP combo changed
 */
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

            targetIPString = ui->lineEdit_targetIP->text();
            targetPortString = ui->lineEdit_targetPort->text();

            ui->lineEdit_targetIP->clear();
            ui->lineEdit_targetIP->setDisabled(true);
            ui->lineEdit_targetPort->clear();
            ui->lineEdit_targetPort->setDisabled(true);

            ui->lineEdit_listenPort->setText(listenPortString);
            ui->lineEdit_listenPort->setDisabled(false);
        }
        else if (tcptype == CLIENT)
        {
            type = TCPCLIENT;
            ui->startButton->setText("Connect");

            listenPortString = ui->lineEdit_listenPort->text();
            ui->lineEdit_listenPort->clear();
            ui->lineEdit_listenPort->setDisabled(true);

            ui->lineEdit_targetIP->setText(targetIPString);
            ui->lineEdit_targetIP->setDisabled(false);
            ui->lineEdit_targetPort->setText(targetPortString);
            ui->lineEdit_targetPort->setDisabled(false);
        }
        ui->comboBox_serverClient->setDisabled(false);
        break;
    case UDP:
        type = UDPSERVER;
        ui->startButton->setText("Start");
        ui->comboBox_serverClient->setDisabled(true);
        ui->lineEdit_listenPort->setText(listenPortString);
        ui->lineEdit_listenPort->setDisabled(false);
        ui->lineEdit_targetIP->setText(targetIPString);
        ui->lineEdit_targetIP->setDisabled(false);
        ui->lineEdit_targetPort->setText(targetPortString);
        ui->lineEdit_targetPort->setDisabled(false);
        break;
    }
}

/*
 * When Server/Client combo changed
 */
void MainWindow::onServerClientComboChanged(int index)
{
    switch (index)
    {
    case SERVER:
        type = TCPSERVER;
        ui->startButton->setText("Start");

        targetIPString = ui->lineEdit_targetIP->text();
        targetPortString = ui->lineEdit_targetPort->text();

        ui->lineEdit_targetIP->clear();
        ui->lineEdit_targetIP->setDisabled(true);
        ui->lineEdit_targetPort->clear();
        ui->lineEdit_targetPort->setDisabled(true);

        ui->lineEdit_listenPort->setText(listenPortString);
        ui->lineEdit_listenPort->setDisabled(false);
        break;
    case CLIENT:
        type = TCPCLIENT;
        ui->startButton->setText("Connect");
        listenPortString = ui->lineEdit_listenPort->text();
        ui->lineEdit_listenPort->clear();
        ui->lineEdit_listenPort->setDisabled(true);

        ui->lineEdit_targetIP->setText(targetIPString);
        ui->lineEdit_targetIP->setDisabled(false);
        ui->lineEdit_targetPort->setText(targetPortString);
        ui->lineEdit_targetPort->setDisabled(false);
        break;
    }
}
