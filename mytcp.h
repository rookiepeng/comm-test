#ifndef MYTCP_H
#define MYTCP_H

#include <QTcpSocket>

class MyTCP : public QTcpSocket
{
    Q_OBJECT
public:
    explicit MyTCP(QObject *parent = nullptr);

signals:

public slots:

private:
    QTcpSocket *tcpSocket;
};

#endif // MYTCP_H
