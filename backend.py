#-!- coding=utf-8 -!-

from querycache import QueryCache
from codemap import CodeMap

def __load_code_map( file_path ) :
    """
    load code map from a file
    """
    from marshal import loads
    file = open( file_path, "r" )
    byte_stream = file.read()
    file.close()
    entry = loads( byte_stream )
    code_map = CodeMap()
    code_map.entry = entry
    return code_map

load_code_map = __load_code_map

class Backend() :
    def __init__( self ) :
        """
        phrase mutli query_cache
        previous the interface to frontend
        """
        self.code_map = load_code_map( "dict/dict.0" )
        self.code = ""
        self.cand = [ -1, 0, [] ]
        self.cache = []
        self.filter = ""
    def reset( self ) :
        self.code = ""
        self.cand = [ -1, 0, [] ]
        self.cache = []
        self.filter = ""
    def append( self, code ) :
        """
        append a code
        will gen cache and put in to cache_stack if the code is vaild
        """
        code = self.code + code
        cache = QueryCache( self.code_map, code )
        flag = cache.vaild()
        if flag :
            self.code = code
            self.cache.append( cache )
            self.cand = [ len( self.cache ) - 1, 0, [] ]
        return flag
    def pop( self ) :
        """
        pop a code
        will pop cache from cache_stack
        """
        if len( self.code ) > 0 :
            self.code = self.code[:-1]
            self.cache.pop()
            self.cand = [ len( self.cache ) - 1, 0, [] ]
    def get_prop( self, cand_index ) :
        """
        get node prot by self cand_list index
        return code, pinyin, hanzi, freq
        """
        cache_index = self.cand[2][cand_index][0]
        cache_cand_index = self.cand[2][cand_index][1]
        cache = self.cache[cache_index]
        return cache.get_prop( cache_cand_index )

    def __gen_cand_list( self, request_length ) :
        """
        gen cand_list, include current query_cache
        and shooter but completed path cache
        will do nothing if request_length too long or too small
        """
        cand_list_length = 0
        if len( self.cache ) > 0 :
            cand_list_length = len( self.cand[2] )
            if cand_list_length < request_length :
                if self.filter == "" :
                    #gen cand list without filter
                    cache_index = self.cand[0]
                    flag = False
                    while cache_index >= 0 and ( not flag ):
                        cache_cand_list_length = self.cand[1]
                        cache = self.cache[cache_index]
                        cache_request_length = cache_cand_list_length + request_length - cand_list_length #compute how many cand need gen
                        new_cache_cand_list_length = cache.gen_cand_list( cache_request_length )
                        if new_cache_cand_list_length - cache_cand_list_length > cache_request_length :
                            new_cache_cand_list_length = cache_cand_list_length + cache_request_length #maybe the cache has gen too long cand, cut it
                        for i in range( cache_cand_list_length, new_cache_cand_list_length ) :
                            #print i, cache_index
                            self.cand[2].append( [ cache_index, i ] ) #append cand node
                        if new_cache_cand_list_length - cache_cand_list_length + cand_list_length < request_length :
                            #need more cand
                            while cache_index >= 0 :
                                cache_index = cache_index - 1
                                cache = self.cache[cache_index]
                                if cache.completed() :
                                    self.cand[0] = cache_index
                                    self.cand[1] = 0
                                    break
                        else :
                            flag = True
                            self.cand[1] = new_cache_cand_list_length
                            cand_list_length = len( self.cand[2] )
                else :
                    #gen cand list with filter
                    pass
        return cand_list_length
    def get_cand( self, start_index, length ) :
        """
        get cand by start_index with length
        will gen cand if needed
        """
        end_pos = start_index + length
        cand_list_length = self.__gen_cand_list( end_pos )
        if end_pos > cand_list_length :
            end_pos = cand_list_length
        if start_index > cand_list_length :
            start_index = cand_list_length
        #result = []
        #print self.cand[2], start_index, end_pos
        #result.extend( self.cand[2][ start_index : end_pos ] )
        result = range( start_index, end_pos )
        return result
    def select( self, cand_index ):
        cache_index = self.cand[2][cand_index][0]
        cache_cand_index = self.cand[2][cand_index][1]
        cache = self.cache[cache_index]
        code, hanzi, pinyin, freq = cache.get_prop( cache_cand_index )
        print code, hanzi, pinyin, freq
        code, hanzi, pinyin, freq = cache.get_prop( cache_cand_index / 2 )
        print code, hanzi, pinyin, freq
    def t() :
        if index < len( cand_list ) :
            node = cand_list[index]
            pinyin_index = node[0]
            node_index = node[1]

            query_result = query_cache[1]
            pinyin_list = query_result[pinyin_index]

            node_list = pinyin_list[2]
            node = node_list.pop( node_index )
            #print node[0], node[1]
            node[1] = new_freq
            #print node[0], node[1]

            node_index = 0
            flag = False
            while node_index < len( node_list ) and ( not flag ) :
                if new_freq > node_list[node_index][1] :
                    flag = True
                else :
                    node_index = node_index + 1
            node_list.insert( node_index, node )
            #for node in node_list :
                #print node[0], node[1]
    def save( self ) :
        pass

