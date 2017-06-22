/*
//    mytcpserver.h
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

#ifndef MYTCPCLIENT_H
#define MYTCPCLIENT_H

#include <QTcpSocket>
#include <QTcpServer>

class MyTCPClient : public QTcpSocket
{
    Q_OBJECT
public:
    explicit MyTCPClient(QObject *parent = nullptr);
    void connectTo(QHostAddress addr, qint16 port);

private slots:
    void onConnected();
    void onDisconnected();
    void messageReady();

private:
    QTcpSocket *tcpSocket;
};

#endif // MYTCPCLIENT_H
