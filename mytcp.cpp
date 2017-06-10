#include "mytcp.h"

MyTCP::MyTCP(QObject *parent) : QTcpSocket(parent)
{
    tcpSocket=new QTcpSocket(this);
}
