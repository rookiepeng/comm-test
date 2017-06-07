#ifndef MYUDP_H
#define MYUDP_H

#include <QUdpSocket>

class MyUDP: public QUdpSocket
{
    Q_OBJECT
public:
    MyUDP(QObject *parent = 0);
    void bindPort(int port);

signals:
    void newMessage(const QString &from, const QString &message);
    void bindSuccess(bool isBinded);

public slots:
    void readyRead();
    void sendMessage(QString string);

private:
    QUdpSocket *socket;
    bool isBinded;
};

#endif // MYUDP_H
