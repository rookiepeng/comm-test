#include "mytcp.h"

MyTCP::MyTCP(QObject *parent) : QTcpSocket(parent)
{
    tcpSocket=new QTcpSocket(this);
}

void MyTCP::doConnect()
{
    tcpSocket = new QTcpSocket(this);

    connect(tcpSocket, SIGNAL(connected()),this, SLOT(connected()));
    connect(tcpSocket, SIGNAL(disconnected()),this, SLOT(disconnected()));
    connect(tcpSocket, SIGNAL(bytesWritten(qint64)),this, SLOT(bytesWritten(qint64)));
    connect(tcpSocket, SIGNAL(readyRead()),this, SLOT(readyRead()));

    qDebug() << "connecting...";

    // this is not blocking call
    tcpSocket->connectToHost("google.com", 80);

    // we need to wait...
    if(!tcpSocket->waitForConnected(5000))
    {
        qDebug() << "Error: " << tcpSocket->errorString();
    }
}

void MyTCP::connected()
{
    qDebug() << "connected...";

    // Hey server, tell me about you.
    tcpSocket->write("HEAD / HTTP/1.0\r\n\r\n\r\n\r\n");
}

void MyTCP::disconnected()
{
    qDebug() << "disconnected...";
}

void MyTCP::bytesWritten(qint64 bytes)
{
    qDebug() << bytes << " bytes written...";
}

void MyTCP::readyRead()
{
    qDebug() << "reading...";

    // read the data from the socket
    qDebug() << tcpSocket->readAll();
}
