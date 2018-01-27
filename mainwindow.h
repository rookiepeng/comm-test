/*
 *   mainwindow.h: header file of mainwindow.cpp
 * 
 *   Copyright (C) 2017  Zhengyu Peng, https://zpeng.me
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program.  If not, see <http://www.gnu.org/licenses/>.
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

#define TCPSERVER 10
#define TCPCLIENT 20
#define UDPSERVER 30
#define APPVERSION "V1.2"

namespace Ui
{
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

  private slots:

    /******************************************************************************
     *
     * TCP Client
     *
     ******************************************************************************/
    void onTcpClientButtonClicked();
    void onTcpClientNewConnection(const QString &from, quint16 port);
    void onTcpClientStopButtonClicked();
    void onTcpClientTimeOut();
    void onTcpClientDisconnectButtonClicked();
    void onTcpClientDisconnected();
    void onTcpClientSendMessage();
    void onTcpClientAppendMessage(const QString &from, const QString &message);

    /******************************************************************************
     *
     * TCP Server
     *
     ******************************************************************************/
    void onTcpServerButtonClicked();
    void onTcpServerNewConnection(const QString &from, quint16 port);
    void onTcpServerStopButtonClicked();
    void onTcpServerDisconnectButtonClicked();
    void onTcpServerDisconnected();
    void onTcpServerSendMessage();
    void onTcpServerAppendMessage(const QString &from, const QString &message);

    /******************************************************************************
     *
     * UDP
     *
     ******************************************************************************/
    void onUdpButtonClicked();
    void onUdpStopButtonClicked();
    void onUdpSendMessage();
    void onUdpAppendMessage(const QString &from, const QString &message);

    void onRefreshButtonClicked();

  public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

  protected:
    void closeEvent(QCloseEvent *event);

  private:
    Ui::MainWindow *ui;
    void initUI();
    void loadSettings();
    void saveSettings();
    void findLocalIPs();
    bool setupConnection(quint8 type);

    void restoreWindowState();

    QTextTableFormat tableFormat;

    MyUDP *myudp = nullptr;
    MyTCPServer *mytcpserver = nullptr;
    MyTCPClient *mytcpclient = nullptr;

    QHostAddress tcpClientTargetAddr;
    quint16 tcpClientTargetPort;

    QHostAddress localAddr;

    quint16 tcpServerListenPort;

    quint16 udpListenPort;
    QHostAddress udpTargetAddr;
    quint16 udpTargetPort;

    QString settingsFileDir;
    QList<QNetworkInterface> interfaceList;
    quint8 type;

    QString messageUDP = "[UDP] ";
    QString messageTCP = "[TCP] ";
};

#endif // MAINWINDOW_H
