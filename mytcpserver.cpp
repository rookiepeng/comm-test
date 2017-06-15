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
    tcpServer=new QTcpServer(this);
    if(tcpServer->listen(addr,port))
    {
        qDebug()<<"listern to port:"<<port;
    }
}

//void MyTCPServer::on_newConnection()
//{
//    socket = server->nextPendingConnection();

//    if(socket->state() == QTcpSocket::ConnectedState)
//    {
//        printf("New connection established.\n");
//        qDebug()<<socket->peerAddress();
//    }
//    connect(socket, SIGNAL(disconnected()),
//    this, SLOT(on_disconnected()));
//    connect(socket, SIGNAL(readyRead()),
//    this, SLOT(on_readyRead()));
//}

//void MyTCPServer::on_readyRead()
//{
//    while(socket->canReadLine())
//    {
//        QByteArray ba = socket->readLine();

//        if(strcmp(ba.constData(), "!exit\n") == 0)
//        {
//            socket->disconnectFromHost();
//            break;
//        }
//        printf(">> %s", ba.constData());
//    }
//}

//void MyTCPServer::on_disconnected()
//{
//    printf("Connection disconnected.\n");
//    disconnect(socket, SIGNAL(disconnected()));
//    disconnect(socket, SIGNAL(readyRead()));
//    socket->deleteLater();
//}
