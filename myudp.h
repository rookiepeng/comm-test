#ifndef MYUDP_H
#define MYUDP_H

#include <QUdpSocket>

class MyUDP: public QUdpSocket
{
    Q_OBJECT
public:
    MyUDP(QObject *parent = 0);

signals:

public slots:
    void readyRead();

private:
    QUdpSocket *socket;

};

#endif // MYUDP_H
