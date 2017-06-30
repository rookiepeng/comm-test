/*
//    mytcpclient.cpp
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

#include "mytcpclient.h"

MyTCPClient::MyTCPClient(QObject *parent) : QTcpSocket(parent)
{
}

void MyTCPClient::connectTo(QHostAddress addr, qint16 port)
{
    tcpSocket = new QTcpSocket(this);
    tcpSocket->connectToHost(addr, port);
    connect(tcpSocket, SIGNAL(connected()), this, SLOT(onConnected()));
    connect(tcpSocket,SIGNAL(stateChanged(QAbstractSocket::SocketState)), this, SLOT(onStateChanged(QAbstractSocket::SocketState)));
}

void MyTCPClient::onConnected()
{
    //printf("Connection established.\n");
    //    char buffer[1024];
    //    forever
    //    {
    //        while(tcpSocket->canReadLine())
    //        {
    //            QByteArray ba = tcpSocket->readLine();
    //            //printf("from server: %s", ba.constData());
    //        }
    //        //printf(">> ");
    //        gets(buffer);
    //        int len = strlen(buffer);
    //        buffer[len] = '\n';
    //        buffer[len+1] = '\0';
    //        tcpSocket->write(buffer);
    //        tcpSocket->flush();
    //    }

    disconnect(tcpSocket,SIGNAL(stateChanged(QAbstractSocket::SocketState)), this, SLOT(onStateChanged(QAbstractSocket::SocketState)));
    connect(tcpSocket, SIGNAL(disconnected()), this, SLOT(onDisconnected()));
    connect(tcpSocket, SIGNAL(readyRead()), this, SLOT(messageReady()));
    emit myClientConnected(tcpSocket->peerAddress().toString(), tcpSocket->peerPort());
}

void MyTCPClient::onStateChanged(QAbstractSocket::SocketState state)
{
    disconnect(tcpSocket, SIGNAL(connected()), this, SLOT(onConnected()));
    disconnect(tcpSocket,SIGNAL(stateChanged(QAbstractSocket::SocketState)), this, SLOT(onStateChanged(QAbstractSocket::SocketState)));
    switch(state)
    {
    case QAbstractSocket::UnconnectedState:
        emit connectionFailed();
        qDebug()<<"connecting timeout";
        break;
    case QAbstractSocket::HostLookupState:
        break;
    case QAbstractSocket::ConnectingState:
        break;
    case QAbstractSocket::ConnectedState:
        break;
    case QAbstractSocket::BoundState:
        break;
    case QAbstractSocket::ListeningState:
        break;
    case QAbstractSocket::ClosingState:
        break;
    }
}

void MyTCPClient::onDisconnected()
{
    disconnect(tcpSocket, SIGNAL(disconnected()));
    disconnect(tcpSocket, SIGNAL(readyRead()));
    //tcpSocket->disconnectFromHost();
    tcpSocket->close();
    tcpSocket->deleteLater();
    emit myClientDisconnected();
}

void MyTCPClient::cleanClient()
{
    tcpSocket->close();
    tcpSocket->deleteLater();
}

void MyTCPClient::messageReady()
{
    array = tcpSocket->readAll();
    emit newMessage(tcpSocket->peerAddress().toString(), array);
}

void MyTCPClient::sendMessage(QString string)
{
    QByteArray Data;
    Data.append(string);
    if (tcpSocket->state() == QTcpSocket::ConnectedState)
    {
        tcpSocket->write(Data);
        tcpSocket->flush();
    }
}

void MyTCPClient::disconnectCurrentConnection()
{
    tcpSocket->disconnectFromHost();
    qDebug() << "disconnectCurrentConnection";
    //    disconnect(tcpSocket, SIGNAL(disconnected()));
    //    disconnect(tcpSocket, SIGNAL(readyRead()));
    //    emit myServerDisconnected();
    //    tcpSocket->close();
    //    tcpSocket->deleteLater();
}
