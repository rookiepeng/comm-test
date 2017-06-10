/*
//    mydup.h
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

#ifndef MYUDP_H
#define MYUDP_H

#include <QUdpSocket>

class MyUDP : public QUdpSocket
{
    Q_OBJECT
public:
    MyUDP(QObject *parent = 0);
    void bindPort(QHostAddress addr, qint16 port);
    void unBind();

signals:
    void newMessage(const QString &from, const QString &message);
    void bindSuccess(bool isBinded);

public slots:
    void readyRead();
    void sendMessage(QHostAddress sender, quint16 senderPort, QString string);

private:
    QUdpSocket *socket;
    bool isBinded;
};

#endif // MYUDP_H
