#include "myudp.h"

MyUDP::MyUDP(QObject *parent)
    : QUdpSocket(parent)
{
    socket = new QUdpSocket(this);
    QHostAddress Addr("127.0.0.1");

    // The most common way to use QUdpSocket class is
    // to bind to an address and port using bind()
    // bool QAbstractSocket::bind(const QHostAddress & address,
    //     quint16 port = 0, BindMode mode = DefaultForPlatform)  
}

void MyUDP::bindPort(int port)
{
    //QHostAddress Addr("127.0.0.1");
    isBinded=socket->bind(QHostAddress::LocalHost, port);
    emit bindSuccess(isBinded);
    connect(socket, SIGNAL(readyRead()), this, SLOT(readyRead()));
}

void MyUDP::sendMessage(QString string)
{
    QByteArray Data;
    Data.append(string);

    // Sends the datagram datagram
    // to the host address and at port.
    // qint64 QUdpSocket::writeDatagram(const QByteArray & datagram,
    //                      const QHostAddress & host, quint16 port)
    socket->writeDatagram(Data, QHostAddress::LocalHost, 1234);
}

void MyUDP::readyRead()
{
    // when data comes in
    QByteArray buffer;
    buffer.resize(socket->pendingDatagramSize());

    QHostAddress sender;
    quint16 senderPort;

    // qint64 QUdpSocket::readDatagram(char * data, qint64 maxSize,
    //                 QHostAddress * address = 0, quint16 * port = 0)
    // Receives a datagram no larger than maxSize bytes and stores it in data.
    // The sender's host address and port is stored in *address and *port
    // (unless the pointers are 0).

    socket->readDatagram(buffer.data(), buffer.size(),
                         &sender, &senderPort);

    emit newMessage(sender.toString(), buffer);

    //qDebug() << "Message from: " << sender.toString();
    //qDebug() << "Message port: " << senderPort;
    //qDebug() << "Message: " << buffer;
}

void MyUDP::unBind()
{
    socket->close();

    if(!socket->isOpen())
    {
        qDebug() << "socket closed";
    }
    socket->deleteLater();
}
