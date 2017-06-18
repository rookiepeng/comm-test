/*
//    mainwindow.h
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

#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QTextTable>
#include <QScrollBar>
#include <QSettings>
#include <QNetworkInterface>

#include "myudp.h"
#include "mytcpserver.h"
#include "mytcpclient.h"

#define TCP 0
#define UDP 1
#define SERVER 0
#define CLIENT 1

namespace Ui
{
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public slots:
    void appendMessage(const QString &from, const QString &message);

private slots:
    void sendMessage();
    void udpBinded(bool isBinded);
    void enableUpdateButton();
    void updateConfig();
    void disableComboBox(int index);

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

private:
    Ui::MainWindow *ui;
    void initUI();
    void loadSettings();
    void saveSettings();
    void findLocalIPs();
    void setupConnection();
    qint16 getProtocolValue();
    qint16 getRoleValue();

    QList<QString> TCPUDPComboList=QList<QString>()<< "TCP"<< "UDP";
    QList<QString> ServerClientComboList=QList<QString>()<< "Server"<< "Client";

    QTextTableFormat tableFormat;
    MyUDP *myudp;
    MyTCPServer *mytcpserver;
    MyTCPClient *mytcpclient;
    QHostAddress targetAddr;
    QHostAddress localAddr;
    quint16 targetPort;
    QString settingsFileDir;
    QList<QNetworkInterface> wifiList;
};

#endif // MAINWINDOW_H
