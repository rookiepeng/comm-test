/****************************************************************************************
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
*****************************************************************************************/

#include "mytcpserver.h"

MyTCPServer::MyTCPServer(QObject *parent) : QTcpServer(parent)
{
    tcpServer = new QTcpServer();
}

bool MyTCPServer::listen(QHostAddress addr, quint16 port)
{
    bool isSuccess=false;
    isSuccess = tcpServer->listen(addr, port);
    if (isSuccess)
    {
        connect(tcpServer, SIGNAL(newConnection()), this, SLOT(onConnected()));
    }
    return isSuccess;
}

void MyTCPServer::onConnected()
{
    disconnect(tcpServer, SIGNAL(newConnection()), this, SLOT(onConnected()));
    tcpSocket = tcpServer->nextPendingConnection();
    if (tcpSocket->state() == QTcpSocket::ConnectedState)
    {
        clientAddr = tcpSocket->peerAddress();
        clientPort = tcpSocket->peerPort();
        connect(tcpSocket, SIGNAL(disconnected()), this, SLOT(onDisconnected()));
        connect(tcpSocket, SIGNAL(readyRead()), this, SLOT(messageReady()));
        emit myServerConnected(tcpSocket->peerAddress().toString(), tcpSocket->peerPort());
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
    emit newMessage(tcpSocket->peerAddress().toString(), array);
}

void MyTCPServer::onDisconnected()
{
    disconnect(tcpSocket, SIGNAL(disconnected()));
    disconnect(tcpSocket, SIGNAL(readyRead()));
    emit myServerDisconnected();
    tcpSocket->close();
    tcpSocket->deleteLater();
    connect(tcpServer, SIGNAL(newConnection()), this, SLOT(onConnected()));
}

void MyTCPServer::stopConnection()
{
    tcpSocket->disconnectFromHost();
}

void MyTCPServer::stopListening()
{
    if (tcpServer->isListening())
    {
        disconnect(tcpServer, SIGNAL(newConnection()), this, SLOT(onConnected()));
        tcpServer->close();
    }
}
