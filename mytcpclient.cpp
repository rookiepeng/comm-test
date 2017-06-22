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
    tcpSocket=new QTcpSocket(this);
    tcpSocket->connectToHost(addr, port);
    connect(tcpSocket, SIGNAL(connected()),this, SLOT(onConnected()));
}

void MyTCPClient::onConnected()
{
    //printf("Connection established.\n");
    char buffer[1024];
    forever
    {
        while(tcpSocket->canReadLine())
        {
            QByteArray ba = tcpSocket->readLine();
            //printf("from server: %s", ba.constData());
        }
        //printf(">> ");
        gets(buffer);
        int len = strlen(buffer);
        buffer[len] = '\n';
        buffer[len+1] = '\0';
        tcpSocket->write(buffer);
        tcpSocket->flush();
    }

    connect(tcpSocket, SIGNAL(disconnected()),this, SLOT(onDisconnected()));
    connect(tcpSocket, SIGNAL(readyRead()),this, SLOT(messageReady()));
}

void MyTCPClient::onDisconnected()
{
    disconnect(tcpSocket, SIGNAL(disconnected()));
    disconnect(tcpSocket, SIGNAL(readyRead()));
    tcpSocket->close();
    tcpSocket->deleteLater();
}

void MyTCPClient::messageReady()
{

}

