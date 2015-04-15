#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <iostream>
#include <memory>
#include <sstream>
#include <algorithm>
#include <string>
#include <vector>
#include <set>
#include <map>
#include <list>
#include <sys/time.h>
#include <unistd.h>

#ifndef foreach
#define foreach(container,it) \
    for(typeof((container).begin()) it = (container).begin();it!=(container).end();++it)
#endif

int main(int argc, char **argv) {
    // 200万在线
    std::map<long long, std::string> mapConns;
    for (size_t i = 0; i < 2000000; ++i) {
        mapConns[i] = "";
    }
    std::list<long long> users;
    for (size_t i = 0; i < 2000000; ++i) {
        users.push_back(i + 324324);
    }

    struct timeval begin_tv;
    gettimeofday(&begin_tv, NULL);


    foreach(users, it) {
        mapConns.find(*it);
    }


    struct timeval now_tv;
    gettimeofday(&now_tv, NULL);
    long long lefttime = ((long long)(now_tv.tv_sec  - begin_tv.tv_sec ) * 1000000 + (now_tv.tv_usec - begin_tv.tv_usec)) / 1000;

    printf("%lld ms\n", lefttime);
    
    return 0;
}
