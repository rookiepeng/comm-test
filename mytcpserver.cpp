/*
//    mytcpserver.cpp
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

#include "mytcpserver.h"

MyTCPServer::MyTCPServer(QObject *parent) : QTcpServer(parent)
{
    //tcpSocket=new QTcpSocket(this);
}

void MyTCPServer::listen(QHostAddress addr, quint16 port)
{
    tcpServer = new QTcpServer(this);
    if (tcpServer->listen(addr, port))
    {
        connect(tcpServer, SIGNAL(newConnection()), this, SLOT(onConnected()));
        qDebug() << "TCP Server: Listern to port " << port;
    }
}

void MyTCPServer::onConnected()
{
    tcpSocket = tcpServer->nextPendingConnection();
    if (tcpSocket->state() == QTcpSocket::ConnectedState)
    {
        clientAddr = tcpSocket->peerAddress();
        clientPort = tcpSocket->peerPort();
        connect(tcpSocket, SIGNAL(disconnected()), this, SLOT(onDisconnected()));
        connect(tcpSocket, SIGNAL(readyRead()), this, SLOT(messageReady()));
        emit myServerConnected(tcpSocket->peerAddress().toString(), tcpSocket->peerPort());
        qDebug() << "TCP Server: New connection from " << tcpSocket->peerAddress().toString();
    }
}

void MyTCPServer::sendMessage(QString string)
{
    QByteArray Data;
    Data.append(string);
    if (tcpSocket->state() == QTcpSocket::ConnectedState)
    {
        tcpSocket->write(Data);
        tcpSocket->flush();
    }
}

void MyTCPServer::messageReady()
{
    array = tcpSocket->readAll();
    //    while(tcpSocket->canReadLine())
    //    {
    //        QByteArray ba = tcpSocket->readLine();

    //        //            if(strcmp(ba.constData(), "!exit\n") == 0)
    //        //            {
    //        //                socket->disconnectFromHost();
    //        //                break;
    //        //            }
    //        qDebug()<<ba.constData();
    //        //printf(">> %s", ba.constData());
    //    }
    emit newMessage(tcpSocket->peerAddress().toString(), array);
    qDebug() << array;
}

void MyTCPServer::onDisconnected()
{
    disconnect(tcpSocket, SIGNAL(disconnected()));
    disconnect(tcpSocket, SIGNAL(readyRead()));
    emit myServerDisconnected();
    tcpSocket->close();
    tcpSocket->deleteLater();
    //tcpServer->close();
    //tcpServer->deleteLater();
}
